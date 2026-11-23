"""
Phase 04 Tests: Evidence Ingestion, Storage Isolation, Human Review, and AI Boundary.
"""
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.ingestion.adapters import AIModelAdapter, ProviderUnavailableError
from app.ingestion.storage import MAX_FILE_SIZE_BYTES, storage
from app.main import app


@pytest.fixture(scope="module")
def client():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    res = client.post("/api/v1/auth/login", json={"phone": "01799998888", "otp": "123456"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_evidence_upload_and_sha256(client, auth_headers):
    content = b"\xe0\xa6\x9a\xe0\xa6\xbe\xe0\xa6\xb2\xe0\xa6\xbe\xe0\xa6\xa8 \xe0\xa7\xaa\xe0\xa7\xa7, \xe0\xa6\xae\xe0\xa7\x87\xe0\xa6\xb8\xe0\xa6\xbe\xe0\xa6\xb0\xe0\xa7\x8d\xe0\xa6\xb8 \xe0\xa6\xb9\xe0\xa6\x95 \xe0\xa6\x9f\xe0\xa7\x8d\xe0\xa6\xb0\xe0\xa7\x87\xe0\xa6\xa1\xe0\xa6\xbe\xe0\xa6\xb0\xe0\xa7\x8d\xe0\xa6\xb8, \xe0\xa6\xa6\xe0\xa6\xbe\xe0\xa6\xac\xe0\xa6\xbf \xe0\xa7\xa8\xe0\xa7\xab,\xe0\xa7\xa6\xe0\xa7\xa6\xe0\xa7\xa6 \xe0\xa6\x9f\xe0\xa6\xbe\xe0\xa6\x95\xe0\xa6\xbe"
    files = {"file": ("invoice_41.txt", io.BytesIO(content), "text/plain")}

    res = client.post("/api/v1/evidence/upload", headers=auth_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert "evidence_id" in data
    assert len(data["content_sha256"]) == 64
    assert data["source_type"] == "text"
    assert data["proposed_party"] is None
    assert data["proposed_amount_paisa"] is None
    assert data["status"] == "needs_review"


def test_evidence_file_size_limit():
    large_content = b"x" * (MAX_FILE_SIZE_BYTES + 1024)
    with pytest.raises(Exception) as exc:
        storage.store_file("tenant-test", "huge.bin", large_content, "application/octet-stream")
    assert "413" in str(exc.value.status_code)


def test_path_traversal_sanitization():
    unsafe_name = "../../etc/passwd"
    sanitized = storage._sanitize_filename(unsafe_name)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert "\\" not in sanitized


def test_human_correction_and_review(client, auth_headers):
    content = b"Haque Traders Invoice 41"
    files = {"file": ("bill.txt", io.BytesIO(content), "text/plain")}

    upload_res = client.post("/api/v1/evidence/upload", headers=auth_headers, files=files).json()
    evidence_id = upload_res["evidence_id"]
    claim_id = upload_res["claim_id"]

    # Owner corrects amount to 2200000 paisa (BDT 22,000) and updates status
    patch_res = client.patch(
        f"/api/v1/evidence/{evidence_id}/claims/{claim_id}",
        headers=auth_headers,
        json={
            "corrected_amount_paisa": 2200000,
            "corrected_party_name": "মেসার্স হক ট্রেডার্স লিমিটেড",
            "status": "corrected",
        },
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert patch_data["effective_amount_paisa"] == 2200000
    assert patch_data["effective_party_name"] == "মেসার্স হক ট্রেডার্স লিমিটেড"
    assert patch_data["is_reviewed"] is True

    # Verify persistence via get
    get_res = client.get(f"/api/v1/evidence/{evidence_id}", headers=auth_headers)
    assert get_res.status_code == 200
    details = get_res.json()
    claim = details["claims"][0]
    assert claim["amount_paisa"] == 2200000
    assert claim["is_reviewed"] is True


def test_ai_boundary_missing_key_behavior():
    """Verifies that missing API key reports unconfigured and does not fabricate live answers."""
    adapter = AIModelAdapter(api_key="")
    assert adapter.is_configured() is False

    # For unknown content, adapter explicitly returns None fields instead of zero or hallucinated defaults
    unknown = adapter.parse_bangla_document("random unformatted scribble", source_type="text")
    assert unknown.amount_paisa is None
    assert unknown.party_name is None
    assert unknown.invoice_ref is None
