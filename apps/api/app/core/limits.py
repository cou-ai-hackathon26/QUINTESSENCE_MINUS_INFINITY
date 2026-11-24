"""Bounded single-process admission. Deployment intentionally uses one API worker."""
import time
from collections import OrderedDict
from threading import Lock
from fastapi import HTTPException
from starlette.responses import JSONResponse

MAX_WINDOWS = 5000
_lock = Lock()
_windows: OrderedDict[str, tuple[float, int, int]] = OrderedDict()


def admit(scope: str, limit: int, seconds: int = 60):
    now = time.monotonic()
    with _lock:
        for key, entry in list(_windows.items()):
            started = entry[0]
            ttl = entry[1] if len(entry) == 3 else seconds
            if now - started >= ttl:
                del _windows[key]
        if scope in _windows:
            entry = _windows[scope]
            start = entry[0]
            count = entry[-1]
            if now - start >= seconds:
                start, count = now, 0
        else:
            start, count = now, 0
        if count >= limit:
            retry_after = max(1, int(seconds - (now - start)))
            raise HTTPException(429, 'Request limit reached. Retry later.', headers={'Retry-After': str(retry_after)})
        if scope not in _windows and len(_windows) >= MAX_WINDOWS:
            _windows.popitem(last=False)
        _windows[scope] = (start, seconds, count + 1)
        _windows.move_to_end(scope)


class BodyLimitMiddleware:
    def __init__(self, app, maximum: int):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        headers = dict(scope.get('headers', []))
        try:
            declared = int(headers.get(b'content-length', b'0'))
        except ValueError:
            declared = self.maximum + 1
        if declared < 0 or declared > self.maximum:
            return await JSONResponse({'detail': 'Request body exceeds the upload limit.'}, status_code=413)(scope, receive, send)

        chunks = []
        total = 0
        more_body = True
        while more_body:
            message = await receive()
            if message.get('type') == 'http.disconnect':
                chunks.append(message)
                break
            body_bytes = message.get('body', b'')
            total += len(body_bytes)
            if total > self.maximum:
                return await JSONResponse({'detail': 'Request body exceeds the upload limit.'}, status_code=413)(scope, receive, send)
            chunks.append(message)
            more_body = bool(message.get('more_body', False))

        async def replay_receive():
            if chunks:
                return chunks.pop(0)
            return await receive()

        await self.app(scope, replay_receive, send)
