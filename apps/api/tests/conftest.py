"""Offline tests must never consume a developer's configured provider credentials."""
import pytest
from app.core.config import settings

@pytest.fixture(autouse=True)
def isolate_external_inference(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','')
    monkeypatch.setattr(settings,'GEMINI_API_KEY','')
