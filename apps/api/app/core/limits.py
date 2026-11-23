"""Bounded single-process admission. Deployment intentionally uses one API worker."""
import time
from threading import Lock
from fastapi import HTTPException

_lock = Lock()
_windows = {}


def admit(scope: str, limit: int, seconds: int = 60):
    now = time.monotonic()
    with _lock:
        for key, (started, _) in list(_windows.items()):
            if now - started >= seconds:
                del _windows[key]
        start, count = _windows.get(scope, (now, 0))
        if count >= limit or len(_windows) > 5000:
            raise HTTPException(429, 'Request limit reached. Retry later.', headers={'Retry-After': str(seconds)})
        _windows[scope] = (start, count + 1)


class BodyLimitMiddleware:
    def __init__(self, app, maximum: int):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        total = 0
        headers = dict(scope.get('headers', []))
        try:
            declared = int(headers.get(b'content-length', b'0'))
        except ValueError:
            declared = self.maximum + 1
        if declared < 0 or declared > self.maximum:
            from starlette.responses import JSONResponse
            return await JSONResponse({'detail': 'Request body exceeds the upload limit.'}, status_code=413)(scope, receive, send)
        async def bounded_receive():
            nonlocal total
            message = await receive()
            total += len(message.get('body', b''))
            if total > self.maximum:
                raise HTTPException(413, 'Request body exceeds the upload limit.')
            return message
        await self.app(scope, bounded_receive, send)
