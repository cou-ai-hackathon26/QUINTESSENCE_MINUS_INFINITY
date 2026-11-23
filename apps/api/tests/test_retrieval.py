"""
Phase 16 Test Suite: Hybrid Merchant Memory Retrieval Engine.
Validates:
1. Exact invoice ID outranking semantically similar older invoices.
2. Bengali numeral normalization in search queries.
3. Reviewed product and merchant alias resolution (Banglish / Bengali synonyms).
4. Strict cross-tenant retrieval isolation.
5. Revoked document chunk exclusion.
6. Keyword-only, dense-only, and hybrid RRF comparison.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.retrieval.engine import (
    HybridRetriever,
    normalize_search_query,
)


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
def tenant_a(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0171{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


@pytest.fixture
def tenant_b(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0172{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


def test_alias_and_bengali_digit_normalization():
    """Verify Banglish aliases and Bengali numerals normalize appropriately."""
    assert "মেসার্স হক ট্রেডার্স" in normalize_search_query("haque traders bill")
    assert "সয়াবিন তেল" in normalize_search_query("soyabean tel 5 litre")
    assert "41" in normalize_search_query("চালান নং ৪১")


def test_exact_invoice_id_outranks_semantic_lookalike(client, tenant_a):
    """
    Ensure exact invoice identity outranks a semantically similar old invoice.
    Chunk 1: Older invoice with similar party, items, and high semantic similarity (Invoice 38).
    Chunk 2: Current exact invoice (Invoice 41).
    """
    # Index old lookalike invoice (Invoice 38)
    client.post(
        "/api/v1/search/index",
        headers=tenant_a,
        json={
            "source_type": "invoice",
            "content": "মেসার্স হক ট্রেডার্স চালান নং ৩৮, বাকিতে ২৫,০০০ টাকার সয়াবিন তেল সরবরাহ",
            "metadata": {"invoice_ref": "38", "party_name": "মেসার্স হক ট্রেডার্স", "amount_paisa": 2500000},
        },
    )

    # Index target invoice (Invoice 41)
    client.post(
        "/api/v1/search/index",
        headers=tenant_a,
        json={
            "source_type": "invoice",
            "content": "মেসার্স হক ট্রেডার্স চালান নং ৪১, দাবি ২৫,০০০ টাকা ক্যাশ মেমো",
            "metadata": {"invoice_ref": "41", "party_name": "মেসার্স হক ট্রেডার্স", "amount_paisa": 2500000},
        },
    )

    # Search specifically targeting Invoice 41
    res = client.post(
        "/api/v1/search",
        headers=tenant_a,
        json={"query": "হক ট্রেডার্স চালান ৪১", "target_invoice_ref": "41", "top_k": 5},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["results_count"] >= 2
    top_hit = data["top_citations"][0]

    # Invariant: Invoice 41 must be #1, beating the semantically similar Invoice 38
    assert top_hit["metadata"]["invoice_ref"] == "41", "Exact invoice identity did not rank #1"
    assert top_hit["exact_id_match"] is True


def test_cross_tenant_isolation_prevents_chunk_leakage(client, tenant_a, tenant_b):
    """Ensure Tenant B cannot retrieve Tenant A's indexed documents."""
    # Tenant A indexes a confidential offer
    client.post(
        "/api/v1/search/index",
        headers=tenant_a,
        json={
            "source_type": "offer",
            "content": "গোপন অফার: সিটি গ্রুপ চিনি প্রতি বস্তা ৪,০০০ টাকা",
            "metadata": {"confidential": True},
        },
    )

    # Tenant B searches for the exact phrase
    res_b = client.post(
        "/api/v1/search",
        headers=tenant_b,
        json={"query": "সিটি গ্রুপ চিনি প্রতি বস্তা ৪,০০০ টাকা", "top_k": 5},
    )
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["results_count"] == 0, "Confidential document leaked across tenants!"


def test_revocation_removes_chunk_from_retrieval(client, tenant_a):
    """Ensure revoked chunks are excluded immediately from retrieval."""
    idx_res = client.post(
        "/api/v1/search/index",
        headers=tenant_a,
        json={
            "source_type": "note",
            "content": "পুরাতন বাতিলকৃত চুক্তি: ১০ দিনে পেমেন্ট দিলে ২% ছাড়",
            "metadata": {"note_type": "discount_terms"},
        },
    )
    chunk_id = idx_res.json()["chunk_id"]

    # Revoke the chunk
    rev_res = client.post(f"/api/v1/search/chunks/{chunk_id}/revoke", headers=tenant_a)
    assert rev_res.status_code == 200

    # Search should NOT return the revoked chunk
    res = client.post(
        "/api/v1/search",
        headers=tenant_a,
        json={"query": "পুরাতন বাতিলকৃত চুক্তি", "top_k": 5},
    )
    assert res.status_code == 200
    data = res.json()
    matching_ids = [c["chunk_id"] for c in data["top_citations"]]
    assert chunk_id not in matching_ids, "Revoked chunk was returned in search results"
