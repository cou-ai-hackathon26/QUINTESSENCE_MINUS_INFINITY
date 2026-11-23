# Phase 16 Evidence: Hybrid Merchant Memory

**Phase:** 16 — hybrid merchant memory  
**Date:** 2026-11-23  
**Status:** VERIFIED (Migration applied, Hybrid RRF Retriever operational, Exact-ID priority verified, Isolation & Revocation tested)  
**Target Milestone Footer:** `Shongoti-Phase: 16`  

---

## 1. Scope & Execution Summary

| Task ID | Description | Result | Evidence / Notes |
|---|---|---|---|
| **P16-T01** | Ingestion and Indexing | COMPLETE | Authored Alembic migration `008_hybrid_memory.py` adding `document_chunks` table. Defined `DocumentChunkModel` in `apps/api/app/persistence/models.py`. Ingests source-preserving chunks across invoices, bills, offers, notes, transcripts, and return terms. |
| **P16-T02** | Actual Hybrid Retriever | COMPLETE | Built `HybridRetriever` in `apps/api/app/retrieval/engine.py` combining exact entity matching, lexical token overlap, dense vector similarity, and Reciprocal Rank Fusion (RRF with $k=60$). Enforced exact-ID priority bonus ($+1.0$) so exact invoice IDs always beat semantic look-alikes. |
| **P16-T03** | Evidence Pack & Safe Answer Boundary | COMPLETE | Implemented `EvidencePack` returning top citations, locators, sufficiency flags, and conflict detection. Retrieval outputs inform case assessments without granting direct ledger posting authority. |
| **P16-T04** | Retrieval Evaluation Suite | COMPLETE | Created `apps/api/tests/test_retrieval.py` covering exact invoice ID priority (Invoice 41 vs 38), Bengali numerals ("চালান নং ৪১" -> 41), reviewed Banglish aliases, cross-tenant isolation, and revocation exclusion. Wired `package.json` command `"test:retrieval"`. |

---

## 2. Test Execution Results

### A. Retrieval Evaluation Suite (`pnpm test:retrieval`)
`apps/api/tests/test_retrieval.py`:
- `test_alias_and_bengali_digit_normalization`: PASSED (normalizes "haque traders", "soyabean tel", "চালান নং ৪১")
- `test_exact_invoice_id_outranks_semantic_lookalike`: PASSED (Invoice 41 ranks #1 over semantically similar older Invoice 38)
- `test_cross_tenant_isolation_prevents_chunk_leakage`: PASSED (Tenant B search returns 0 results for Tenant A documents)
- `test_revocation_removes_chunk_from_retrieval`: PASSED (revoked chunks are immediately excluded)

### B. Offline Verification Gate (`node scripts/verify-offline.js`)
- Frontend Typecheck: PASSED
- Domain Golden Contracts (34 tests): PASSED
- API, Persistence & Security Tests (95 tests): PASSED
- Web Unit & Workflow Tests (11 tests): PASSED
- Web Production Build: PASSED
- CSS & Accessibility Static Scan: PASSED
- Security & Secrets Scan (229 files, 0 leaks): PASSED
- Evaluation Benchmark Fixtures (48 cases): PASSED

---

## 3. Acceptance Gate Assessment
All acceptance criteria for Phase 16 under `EXTENSION_PLAN.md` are satisfied:
- Persistent retrieval retrieves the right source/entity/version in the configured database.
- Zero cross-tenant data leakage.
- Exact invoice identity outranks look-alikes.
- Keyword and dense contributions combined deterministically via RRF ($k=60$).
