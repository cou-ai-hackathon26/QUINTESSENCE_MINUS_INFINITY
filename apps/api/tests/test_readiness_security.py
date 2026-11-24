"""Observed readiness failures must remain rejected without breaking valid work."""
import json
import time
from unittest.mock import patch
import jwt
import pytest
from pydantic import ValidationError
from test_workbench_auth import client
from app.core.config import Settings, settings
from app.api.v1 import voice_speak
from app.ai_schemas import GroundedAnswer
from app.groq_provider import GroqProvider
from app.agents.contracts import SpecialistFinding, CitedFinding
from app.agents.real_orchestrator import AgentOrchestrator


def identity(c):
    who = c.post('/api/v1/auth/judge-session', json={}).json()
    return who, {'Authorization': 'Bearer ' + who['access_token']}


def test_private_voice_boundary_cache_failure_and_limits(client, monkeypatch, tmp_path):
    c, _ = client
    monkeypatch.setattr(voice_speak, 'CACHE_DIR', tmp_path)
    calls = []
    class SyntheticSpeech:
        def __init__(self, *args, **kwargs): calls.append(args)
        async def stream(self): yield {'type': 'audio', 'data': b'explicit-test-audio'}
    monkeypatch.setattr(voice_speak.edge_tts, 'Communicate', SyntheticSpeech)
    assert c.post('/api/v1/voice/speak', json={'text': 'Synthetic'}).status_code == 401
    _, headers = identity(c)
    for cache in ['MISS', 'HIT']:
        r = c.post('/api/v1/voice/speak', headers=headers, json={'text': 'Synthetic'})
        assert r.status_code == 200 and r.headers['x-cache'] == cache
        assert r.headers['cache-control'] == 'private, no-store'
    _, headers = identity(c)
    assert c.post('/api/v1/voice/speak', headers=headers, json={'text': 'Synthetic'}).headers['x-cache'] == 'MISS'
    assert len(calls) == 2
    assert c.get('/api/v1/voice/speak', headers=headers, params={'text': 'Synthetic'}).status_code == 405
    assert c.post('/api/v1/voice/speak', headers=headers, json={'text': 'Synthetic', 'voice': 'unknown'}).status_code == 422
    class Failure(SyntheticSpeech):
        async def stream(self):
            raise RuntimeError('private-provider-detail')
            yield
    monkeypatch.setattr(voice_speak.edge_tts, 'Communicate', Failure)
    r = c.post('/api/v1/voice/speak', headers=headers, json={'text': 'Another synthetic request'})
    assert r.status_code == 502 and 'private-provider-detail' not in r.text
    monkeypatch.setattr(voice_speak, 'edge_tts', None)
    assert c.post('/api/v1/voice/speak', headers=headers, json={'text': 'Synthetic'}).status_code == 503


def test_production_default_secret_and_malformed_signed_claims_are_rejected(client):
    with pytest.raises(ValidationError): Settings(_env_file=None, ENVIRONMENT='production', SECRET_KEY='short')
    Settings(_env_file=None, ENVIRONMENT='production', SECRET_KEY='synthetic-test-key-' * 3, ALLOW_LEGACY_TEST_AUTH=False)
    c, _ = client
    who, _ = identity(c)
    token = jwt.encode({'sub': who['user_id'], 'tenant_id': who['tenant_id'], 'role': [], 'exp': int(time.time()) + 60}, settings.SECRET_KEY, algorithm='HS256')
    assert c.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + token}).status_code == 401
    assert c.post('/api/v1/auth/register', headers={'Content-Length': str(settings.API_MAX_BODY_BYTES + 1)}, content=b'{}').status_code == 413


def test_cashier_cannot_confirm_financial_source(client):
    from app.persistence.models import UserModel
    c, factory = client
    who, headers = identity(c)
    uploaded = c.post('/api/v1/evidence/upload', headers=headers, files={'file': ('synthetic.txt', b'No confirmed amount', 'text/plain')}).json()
    with factory() as db:
        db.get(UserModel, who['user_id']).role = 'cashier'
        db.commit()
    r = c.patch('/api/v1/evidence/' + uploaded['evidence_id'] + '/claims/' + uploaded['claim_id'], headers=headers, json={'status': 'confirmed', 'corrected_amount_paisa': 999})
    assert r.status_code == 403


def test_grounded_answer_rejects_false_money_but_keeps_correct_answer(client, monkeypatch):
    c, _ = client
    _, headers = identity(c)
    session = c.post('/api/v1/copilot/sessions', headers=headers, json={}).json()['id']
    monkeypatch.setattr(settings, 'GROQ_API_KEY', 'synthetic-test-only')
    monkeypatch.setattr(settings, 'AI_PROVIDER', 'groq')
    for amount, status in [('999999', 422), ('5000', 200)]:
        with patch.object(GroqProvider, 'generate', return_value=GroundedAnswer(answer='Cash is ' + amount + ' Taka.', cited_source_ids=['ledger/current'])):
            r = c.post(f'/api/v1/copilot/sessions/{session}/messages', headers=headers, json={'query': 'What is my cash balance?'})
            assert r.status_code == status
    with patch.object(GroqProvider, 'generate', return_value=GroundedAnswer(answer='No amount established.', cited_source_ids=['other-tenant/source'])):
        assert c.post(f'/api/v1/copilot/sessions/{session}/messages', headers=headers, json={'query': 'Review this'}).status_code == 422


def test_quote_guard_applies_to_structured_sources(client):
    from app.groq_provider import InferenceUnavailable
    c, factory = client
    who, _ = identity(c)
    with factory() as db:
        run = AgentOrchestrator(db, who['tenant_id'])
        finding = SpecialistFinding(summary='Synthetic', case_facts=None, findings=[CitedFinding(source_id='ledger/current', claim='Synthetic', quote='invented absent quote')])
        with pytest.raises(InferenceUnavailable, match='agent_quote_not_in_source'):
            run._validate_facts(finding, None, [], {'ledger/current': json.dumps({'balance_paisa': 500000})})


def test_rate_limit_and_auth_throttler_resist_state_poisoning_dos(client):
    from app.core.limits import admit, _windows, MAX_WINDOWS
    from app.api.v1.workbench_auth import _attempts, MAX_ATTEMPT_BUCKETS
    _windows.clear()
    for i in range(MAX_WINDOWS + 50):
        admit(f"synthetic-scope-{i}", limit=5, seconds=60)
    assert len(_windows) <= MAX_WINDOWS
    # Legitimate tenant scope still admitted without global 429 lockout
    admit("legitimate-tenant-scope", limit=5, seconds=60)

    c, _ = client
    now = time.monotonic()
    _attempts.clear()
    for i in range(MAX_ATTEMPT_BUCKETS + 50):
        _attempts[f"198.51.100.{i}"] = (now, 1)
    # New login/judge session is not globally locked out by 2000+ spoofed IPs
    res = c.post('/api/v1/auth/judge-session', json={})
    assert res.status_code == 201


def test_handover_enforces_ledger_cash_against_client_fabrication(client):
    c, _ = client
    _, headers = identity(c)
    c.headers['Origin'] = 'http://testserver'
    # Judge workspace has 500,000 paisa in asset:cash. Client tries to claim system_cash_paisa=100,000 to hide 400,000 shortage.
    res = c.post(
        '/api/v1/operations/handovers',
        headers=headers,
        json={
            'shift_name': 'Evening',
            'opened_by': 'Owner',
            'closed_by': 'Cashier',
            'declared_cash_paisa': 100000,
            'system_cash_paisa': 100000,
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body['system_cash_paisa'] == 500000
    assert body['variance_paisa'] == -400000


def test_orphaned_agent_runs_auto_recover_and_do_not_deadlock_tenant(client):
    from datetime import datetime, timedelta, timezone
    from app.persistence.models import AgentRunModel
    from app.agents.real_orchestrator import _ACTIVE_RUNS
    c, factory = client
    who, headers = identity(c)
    c.headers['Origin'] = 'http://testserver'
    stale_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    with factory() as db:
        for idx in range(2):
            r = AgentRunModel(
                id=f"orphaned-run-{idx}-{who['tenant_id'][:8]}",
                tenant_id=who['tenant_id'],
                status='running',
                budget_calls_max=4,
                budget_calls_used=1,
                created_at=stale_time,
            )
            db.add(r)
        db.commit()
    _ACTIVE_RUNS.clear()
    # Starting a new cash_query run must recover the orphaned runs instead of returning 429
    res = c.post('/api/v1/agents/runs', headers=headers, json={'case_type': 'cash_query', 'query': 'Current cash'})
    assert res.status_code == 202


def test_asgi_body_limit_middleware_handles_streamed_oversized_body_cleanly():
    import asyncio
    from fastapi import FastAPI, Request
    from app.core.limits import BodyLimitMiddleware
    from app.core.permissions import verify_tenant_ownership
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        verify_tenant_ownership("tenant-a", "tenant-b")
    assert exc_info.value.status_code == 403

    inner = FastAPI()

    @inner.post("/stream")
    async def _stream(request: Request):
        await request.body()
        return {"ok": True}

    mw = BodyLimitMiddleware(inner, maximum=10)
    sent = []

    async def _run():
        chunks = [
            {"type": "http.request", "body": b"123456", "more_body": True},
            {"type": "http.request", "body": b"789012", "more_body": False},
        ]

        async def receive():
            return chunks.pop(0)

        async def send(msg):
            sent.append(msg)

        scope = {"type": "http", "method": "POST", "path": "/stream", "query_string": b"", "headers": []}
        await mw(scope, receive, send)

    asyncio.run(_run())
    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 413
