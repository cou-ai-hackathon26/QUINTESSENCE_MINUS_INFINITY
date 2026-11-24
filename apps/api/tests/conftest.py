"""Offline tests must never consume a developer's configured provider credentials."""
import os
import shutil
import sys
import uuid
import pytest
from app.core.config import settings
from app.ingestion.storage import storage

if sys.platform == "win32" and sys.version_info >= (3, 13):
    # Python 3.13+ on Windows sets a protected 0o700 DACL on os.mkdir(path, 0o700) that
    # strips inherited sandbox logon SIDs (S-1-4-*), causing immediate PermissionError.
    _orig_mkdir = os.mkdir

    def _sandbox_safe_mkdir(path, mode=0o777, *args, **kwargs):
        return _orig_mkdir(path, 0o777 if mode == 0o700 else mode, *args, **kwargs)

    os.mkdir = _sandbox_safe_mkdir


@pytest.fixture
def tmp_path():
    from pathlib import Path
    p = Path(os.path.abspath(os.path.join(".pytest_evidence_tmp", "tmp_" + uuid.uuid4().hex[:10])))
    os.makedirs(p, exist_ok=True)
    try:
        yield p
    finally:
        shutil.rmtree(p, ignore_errors=True)


@pytest.fixture(autouse=True)
def isolate_external_inference(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','')
    monkeypatch.setattr(settings,'GROQ_API_KEYS','')
    monkeypatch.setattr(settings,'AI_RETRY_MIN_SECONDS',0.0)
    monkeypatch.setattr(settings,'GEMINI_API_KEY','')
    monkeypatch.setattr(settings,'SEMANTIC_ENABLED',False)
    # Legacy test fixtures may construct isolated synthetic identities. Runtime default is disabled.
    monkeypatch.setattr(settings,'ALLOW_LEGACY_TEST_AUTH',True)
    test_storage_root = os.path.abspath(os.path.join(".pytest_evidence_tmp", uuid.uuid4().hex[:10]))
    os.makedirs(test_storage_root, exist_ok=True)
    monkeypatch.setattr(settings, "EVIDENCE_STORAGE_PATH", test_storage_root)
    monkeypatch.setattr(storage, "base_dir", test_storage_root)
    try:
        yield
    finally:
        shutil.rmtree(test_storage_root, ignore_errors=True)
