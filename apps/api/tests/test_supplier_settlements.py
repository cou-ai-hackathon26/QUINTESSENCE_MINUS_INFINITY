from datetime import timedelta

from app.domain.supplier_settlement import OpenInvoice, propose_oldest_due_first, validate_manual_split
from app.persistence.models import (
    AccountModel, AllocationModel, EvidenceModel, ExtractedClaimModel, JournalEntryModel,
    PartyModel, PostingModel, SupplierSettlementModel, now_utc,
)
from test_workbench_auth import client


def test_split_engine_is_exact_deterministic_and_capacity_bounded():
    invoices = [
        OpenInvoice("b", 400000, "2026-11-02", "INV-102", 1),
        OpenInvoice("a", 600000, "2026-11-01", "INV-101", 1),
        OpenInvoice("c", 500000, "2026-11-03", "INV-103", 1),
    ]
    result = propose_oldest_due_first(800000, invoices)
    assert [(line.obligation_id, line.amount_paisa) for line in result.lines] == [("a", 600000), ("b", 200000)]
    assert result.allocated_paisa == 800000 and result.unallocated_paisa == 0
    try:
        validate_manual_split(800000, {row.obligation_id: row for row in invoices}, [("a", 700000), ("b", 100000)])
        assert False, "capacity violation must fail"
    except ValueError as error:
        assert "exceeds" in str(error)


def test_reviewed_settlement_posts_once_and_allocates_invoice_capacity(client):
    c, factory = client
    identity = c.post("/api/v1/auth/judge-session", json={}).json()
    c.headers["Origin"] = "http://testserver"
    supplier = next(row for row in c.get("/api/v1/merchant/parties").json() if row["party_type"] == "supplier")
    created = c.post("/api/v1/supplier-settlements", json={"supplier_party_id": supplier["id"], "amount_paisa": 500000, "channel": "cash", "idempotency_key": "settlement-test-1"})
    assert created.status_code == 200
    settlement = created.json()
    assert [row["invoice_ref"] for row in settlement["invoices"]] == ["INV-101", "INV-102", "INV-103"]
    preview = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/preview", json={"expected_version": settlement["version"]})
    assert preview.status_code == 200
    reviewed = preview.json()
    assert reviewed["status"] == "ready_for_review" and reviewed["allocated_paisa"] == 500000
    assert {line["amount_paisa"] for line in reviewed["lines"]} == {300000, 200000}
    confirmed = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/confirm", json={"expected_version": reviewed["version"], "expected_party_due_paisa": 2500000, "expected_account_balance_paisa": 500000, "confirmed": True})
    assert confirmed.status_code == 200
    result = confirmed.json()
    assert result["status"] == "recorded" and result["journal_entry_id"]
    replay = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/confirm", json={"expected_version": reviewed["version"], "expected_party_due_paisa": 2500000, "expected_account_balance_paisa": 500000, "confirmed": True})
    assert replay.status_code == 200 and replay.json()["journal_entry_id"] == result["journal_entry_id"]
    with factory() as db:
        assert db.query(AllocationModel).filter_by(tenant_id=identity["tenant_id"], source_payment_id=result["journal_entry_id"]).count() == 2
        entry = db.query(JournalEntryModel).filter_by(id=result["journal_entry_id"]).one()
        postings = db.query(PostingModel).filter_by(journal_entry_id=entry.id).all()
        assert sum(p.amount_paisa for p in postings if p.direction == "debit") == 500000
        assert sum(p.amount_paisa for p in postings if p.direction == "credit") == 500000
        party = db.query(PartyModel).filter_by(id=supplier["id"]).one()
        cash = db.query(AccountModel).filter_by(tenant_id=identity["tenant_id"], code="asset:cash").one()
        assert party.current_due_paisa == 2000000 and cash.current_balance_paisa == 0


def test_similar_or_conflicting_names_never_auto_merge(client):
    c, factory = client
    identity = c.post("/api/v1/auth/judge-session", json={}).json()
    c.headers["Origin"] = "http://testserver"
    karim = c.post("/api/v1/merchant/parties", json={"name": "Karim", "party_type": "supplier"}).json()
    karim_traders = c.post("/api/v1/merchant/parties", json={"name": "Karim Traders", "party_type": "supplier"}).json()
    with factory() as db:
        evidence = EvidenceModel(tenant_id=identity["tenant_id"], filename="karim-invoice.png", mime_type="image/png", file_size_bytes=10, content_sha256="a" * 64, storage_path="synthetic-private-path", source_type="image", status="extracted")
        db.add(evidence); db.flush()
        db.add(ExtractedClaimModel(tenant_id=identity["tenant_id"], evidence_id=evidence.id, party_name="Karim Traders", invoice_ref="K-1", amount_paisa=10000, status="proposed", raw_model_response="{}"))
        db.commit(); evidence_id = evidence.id
    settlement = c.post("/api/v1/supplier-settlements", json={"supplier_party_id": karim["id"], "amount_paisa": 10000, "channel": "cash", "idempotency_key": "karim-ambiguous"}).json()
    attached = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence", json={"evidence_id": evidence_id, "document_role": "invoice"}).json()
    link = attached["evidence"][0]
    assert link["party_match_status"] == "conflict"
    assert link["party_candidates"][0]["party_id"] == karim_traders["id"]
    refused = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{link['link_id']}/review", json={"confirmed_party_id": karim["id"], "remember_extracted_name_as_alias": True, "decision": "confirmed"})
    assert refused.status_code == 409
    assert "another registered supplier" in refused.json()["detail"]


def test_unreviewed_source_blocks_recording_and_can_be_explicitly_confirmed(client):
    c, factory = client
    identity = c.post("/api/v1/auth/judge-session", json={}).json()
    c.headers["Origin"] = "http://testserver"
    supplier = next(row for row in c.get("/api/v1/merchant/parties").json() if row["party_type"] == "supplier")
    with factory() as db:
        evidence = EvidenceModel(tenant_id=identity["tenant_id"], filename="cropped.png", mime_type="image/png", file_size_bytes=10, content_sha256="b" * 64, storage_path="synthetic-private-path", source_type="image", status="needs_review")
        db.add(evidence); db.flush()
        db.add(ExtractedClaimModel(tenant_id=identity["tenant_id"], evidence_id=evidence.id, party_name=None, invoice_ref=None, amount_paisa=10000, status="proposed", raw_model_response='{"extraction_error":"unreadable_reference"}'))
        db.commit(); evidence_id = evidence.id
    settlement = c.post("/api/v1/supplier-settlements", json={"supplier_party_id": supplier["id"], "amount_paisa": 10000, "channel": "cash", "idempotency_key": "cropped-review"}).json()
    attached = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence", json={"evidence_id": evidence_id, "document_role": "payment_receipt"}).json()
    preview = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/preview", json={"expected_version": attached["version"]}).json()
    assert preview["status"] == "needs_clarification" and preview["needs_human_review"] is True
    link = preview["evidence"][0]
    reviewed = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{link['link_id']}/review", json={"confirmed_party_id": supplier["id"], "decision": "confirmed"})
    assert reviewed.status_code == 200 and reviewed.json()["needs_human_review"] is False


def test_cropped_receipt_requires_verified_amount(client):
    c, factory = client
    identity = c.post("/api/v1/auth/judge-session", json={}).json()
    c.headers["Origin"] = "http://testserver"
    supplier = next(row for row in c.get("/api/v1/merchant/parties").json() if row["party_type"] == "supplier")
    with factory() as db:
        evidence = EvidenceModel(tenant_id=identity["tenant_id"], filename="cropped-receipt.png", mime_type="image/png", file_size_bytes=10, content_sha256="c" * 64, storage_path="synthetic-private-path", source_type="image", status="needs_review")
        db.add(evidence); db.flush()
        db.add(ExtractedClaimModel(tenant_id=identity["tenant_id"], evidence_id=evidence.id, party_name=supplier["name"], invoice_ref=None, amount_paisa=None, status="proposed", raw_model_response='{"extraction_error":"cropped_amount"}'))
        db.commit(); evidence_id = evidence.id
    settlement = c.post("/api/v1/supplier-settlements", json={"supplier_party_id": supplier["id"], "amount_paisa": 10000, "channel": "cash", "idempotency_key": "cropped-amount"}).json()
    attached = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence", json={"evidence_id": evidence_id, "document_role": "payment_receipt"}).json()
    link = attached["evidence"][0]
    refused = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{link['link_id']}/review", json={"confirmed_party_id": supplier["id"], "decision": "confirmed"})
    assert refused.status_code == 422 and "receipt amount" in refused.json()["detail"]
    corrected = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{link['link_id']}/review", json={"confirmed_party_id": supplier["id"], "decision": "confirmed", "verified_amount_paisa": 10000})
    assert corrected.status_code == 200
    assert corrected.json()["evidence"][0]["extracted_amount_paisa"] == 10000


def test_conflicting_supplier_messages_leave_one_material_question(client):
    c, factory = client
    identity = c.post("/api/v1/auth/judge-session", json={}).json()
    c.headers["Origin"] = "http://testserver"
    supplier = next(row for row in c.get("/api/v1/merchant/parties").json() if row["party_type"] == "supplier")
    evidence_ids = []
    with factory() as db:
        for suffix, amount in (("old", 10000), ("new", 12000)):
            evidence = EvidenceModel(tenant_id=identity["tenant_id"], filename=f"{suffix}-message.png", mime_type="image/png", file_size_bytes=10, content_sha256=("d" if suffix == "old" else "e") * 64, storage_path=f"synthetic-{suffix}", source_type="image", status="extracted")
            db.add(evidence); db.flush()
            db.add(ExtractedClaimModel(tenant_id=identity["tenant_id"], evidence_id=evidence.id, party_name=supplier["name"], invoice_ref="INV-101", amount_paisa=amount, status="proposed", raw_model_response="{}"))
            evidence_ids.append(evidence.id)
        db.commit()
    settlement = c.post("/api/v1/supplier-settlements", json={"supplier_party_id": supplier["id"], "amount_paisa": 10000, "channel": "cash", "idempotency_key": "contradicting-messages"}).json()
    for evidence_id in evidence_ids:
        settlement = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence", json={"evidence_id": evidence_id, "document_role": "supplier_message"}).json()
        link = next(item for item in settlement["evidence"] if item["evidence_id"] == evidence_id)
        settlement = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{link['link_id']}/review", json={"confirmed_party_id": supplier["id"], "decision": "confirmed"}).json()
    preview = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/preview", json={"expected_version": settlement["version"]})
    assert preview.status_code == 200
    assert preview.json()["status"] == "needs_clarification"
    assert preview.json()["needs_human_review"] is True
    assert preview.json()["contradictions"][0]["amounts_paisa"] == [10000, 12000]
    conflict = preview.json()["contradictions"][0]
    ignored = c.post(
        f"/api/v1/supplier-settlements/{settlement['id']}/evidence/{conflict['link_ids'][0]}/review",
        json={"confirmed_party_id": supplier["id"], "decision": "ignored", "remember_extracted_name_as_alias": True},
    )
    assert ignored.status_code == 200
    assert ignored.json()["status"] == "collecting_evidence"
    assert ignored.json()["contradictions"] == []
    ready = c.post(f"/api/v1/supplier-settlements/{settlement['id']}/preview", json={"expected_version": ignored.json()["version"]})
    assert ready.json()["status"] == "ready_for_review"
