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
