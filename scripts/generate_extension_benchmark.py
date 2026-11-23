"""Generates 30 extension paired families (60 cases) for Phase 25 Evaluation Benchmark."""
import json
import os

families = [
    # Buying Desk (Families 25-29)
    {
        "id": 25, "name": "bonus_carton_condition",
        "clean": {"title": "Verified 10 carton bonus", "input": {"sku": "SKU-SOAP", "qty": 10, "bonus_sku": "SKU-SOAP", "bonus_qty": 1}, "expected_cost_paisa": 9090, "confidence_cap": 95},
        "ambiguous": {"title": "Unverified bonus terms", "input": {"sku": "SKU-SOAP", "qty": 10, "bonus_sku": None, "bonus_qty": 1}, "expected_cost_paisa": 10000, "confidence_cap": 59},
    },
    {
        "id": 26, "name": "pack_size_mismatch",
        "clean": {"title": "Standard 500ml pack", "input": {"sku": "SKU-OIL-500ML", "pack_units": 1}, "matched": True, "confidence_cap": 90},
        "ambiguous": {"title": "Collapsed pack size without conversion", "input": {"sku": "SKU-OIL-1L", "pack_units": 2}, "matched": False, "confidence_cap": 59},
    },
    {
        "id": 27, "name": "cash_liquidity_feasibility",
        "clean": {"title": "Sufficient liquid cash for offer", "input": {"order_paisa": 500000, "liquid_cash_paisa": 1000000}, "feasible": True, "confidence_cap": 100},
        "ambiguous": {"title": "Insufficient liquid cash shortfall", "input": {"order_paisa": 1500000, "liquid_cash_paisa": 1000000}, "feasible": False, "shortfall_paisa": 500000, "confidence_cap": 100},
    },
    {
        "id": 28, "name": "negotiation_draft_vs_deal",
        "clean": {"title": "Accepted purchase order", "input": {"status": "confirmed_by_supplier"}, "is_binding": True, "confidence_cap": 95},
        "ambiguous": {"title": "Draft negotiation question", "input": {"status": "draft_negotiation"}, "is_binding": False, "confidence_cap": 59},
    },
    {
        "id": 29, "name": "minimum_order_quantity",
        "clean": {"title": "Order meets MOQ", "input": {"moq": 50, "ordered": 60}, "valid": True, "confidence_cap": 90},
        "ambiguous": {"title": "Order below MOQ", "input": {"moq": 50, "ordered": 30}, "valid": False, "confidence_cap": 59},
    },

    # Receiving & Returns (Families 30-34)
    {
        "id": 30, "name": "delivery_shortage_deduction",
        "clean": {"title": "Full delivery received", "input": {"ordered": 100, "received": 100, "damaged": 0}, "usable_stock": 100, "claim_paisa": 0},
        "ambiguous": {"title": "Shortage with 10 missing", "input": {"ordered": 100, "received": 90, "damaged": 0}, "usable_stock": 90, "claim_paisa": 10000},
    },
    {
        "id": 31, "name": "damaged_goods_isolation",
        "clean": {"title": "Zero damaged items", "input": {"received": 50, "damaged": 0}, "usable_stock": 50, "credit_status": "none"},
        "ambiguous": {"title": "Damaged goods excluded from usable stock", "input": {"received": 50, "damaged": 8}, "usable_stock": 42, "credit_status": "suspected"},
    },
    {
        "id": 32, "name": "credit_note_reuse_prevention",
        "clean": {"title": "First time credit note application", "input": {"credit_id": "CR-01", "status": "accepted_by_supplier"}, "permitted": True},
        "ambiguous": {"title": "Attempted reuse of applied credit note", "input": {"credit_id": "CR-01", "status": "applied_to_bill"}, "permitted": False},
    },
    {
        "id": 33, "name": "return_window_deadline",
        "clean": {"title": "Return within 7-day cutoff", "input": {"days_since_delivery": 4, "cutoff_days": 7}, "returnable": True},
        "ambiguous": {"title": "Return after cutoff expired", "input": {"days_since_delivery": 10, "cutoff_days": 7}, "returnable": False},
    },
    {
        "id": 34, "name": "unreplied_supplier_claim",
        "clean": {"title": "Supplier accepted credit claim", "input": {"reply": "agreed", "credit_amount": 5000}, "claim_status": "accepted_by_supplier"},
        "ambiguous": {"title": "Supplier unreplied dispute remains unresolved", "input": {"reply": None, "credit_amount": 5000}, "claim_status": "suspected"},
    },

    # Demand Memory (Families 35-39)
    {
        "id": 35, "name": "unmet_demand_no_revenue_booking",
        "clean": {"title": "Observed customer request logged", "input": {"product": "Horlicks 500g", "count": 2}, "revenue_booked_paisa": 0, "receivable_paisa": 0},
        "ambiguous": {"title": "Stockout request repeated mention", "input": {"product": "Horlicks 500g", "count": 2, "repeat": True}, "revenue_booked_paisa": 0, "receivable_paisa": 0},
    },
    {
        "id": 36, "name": "stockout_window_zero_sales",
        "clean": {"title": "Item in stock with 0 sales", "input": {"available_stock": 15, "sales": 0}, "is_true_zero_demand": True},
        "ambiguous": {"title": "Stockout item 0 sales is not 0 demand", "input": {"available_stock": 0, "sales": 0}, "is_true_zero_demand": False},
    },
    {
        "id": 37, "name": "cold_start_factual_scenarios",
        "clean": {"title": "Store history >= 14 days", "input": {"history_days": 21}, "provides_probability": False, "mode": "evaluated_rolling"},
        "ambiguous": {"title": "Store history < 14 days factual counts only", "input": {"history_days": 6}, "provides_probability": False, "mode": "observed_factual_scenario"},
    },
    {
        "id": 38, "name": "reorder_pack_rounding",
        "clean": {"title": "Exact carton multiple reorder", "input": {"needed_units": 48, "pack_size": 24}, "order_packs": 2},
        "ambiguous": {"title": "Fractional need rounds up to whole pack", "input": {"needed_units": 50, "pack_size": 24}, "order_packs": 3},
    },
    {
        "id": 39, "name": "demand_alias_deduplication",
        "clean": {"title": "Standard SKU name request", "input": {"raw": "তীর সয়াবিন ১ লিটার"}, "resolved_sku": "SKU-SOYABEAN-1L"},
        "ambiguous": {"title": "Colloquial alias request", "input": {"raw": "তীরের তেল এক বোতল"}, "resolved_sku": "SKU-SOYABEAN-1L"},
    },

    # Compound Voice & Transactions (Families 40-44)
    {
        "id": 40, "name": "split_collection_and_sale",
        "clean": {"title": "Single cash sale utterance", "input": {"transcript": "৫০০ টাকার চিনি নগদ বিক্রি"}, "drafts_count": 1, "revenue_paisa": 50000},
        "ambiguous": {"title": "Compound collection and sale", "input": {"transcript": "করিমের বকেয়া ৫০০ পেলাম আর ২০০ টাকার ডাল বিক্রি"}, "drafts_count": 2, "revenue_paisa": 20000},
    },
    {
        "id": 41, "name": "cash_close_shift_variance",
        "clean": {"title": "Exact matched shift close", "input": {"declared": 500000, "system": 500000}, "variance_paisa": 0, "hypotheses_count": 0},
        "ambiguous": {"title": "Discrepant shift close with hypotheses", "input": {"declared": 480000, "system": 500000}, "variance_paisa": -20000, "hypotheses_count": 1},
    },
    {
        "id": 42, "name": "container_deposit_separation",
        "clean": {"title": "Goods sale without containers", "input": {"goods_paisa": 30000, "container_deposit": 0}, "deposit_held": 0},
        "ambiguous": {"title": "Goods sale with returnable crates", "input": {"goods_paisa": 30000, "container_deposit": 10000}, "deposit_held": 10000},
    },
    {
        "id": 43, "name": "supplier_order_scoped_change",
        "clean": {"title": "Supplier confirm agreed price", "input": {"price_diff": 0}, "review_required": False},
        "ambiguous": {"title": "Supplier proposed price hike for PO", "input": {"price_diff": 200}, "review_required": True, "scope": "scoped_to_order_only"},
    },
    {
        "id": 44, "name": "action_draft_status_guard",
        "clean": {"title": "Action draft reviewed and approved", "input": {"status": "approved"}, "posts_to_ledger": True},
        "ambiguous": {"title": "Action draft in draft status", "input": {"status": "draft"}, "posts_to_ledger": False},
    },

    # Hybrid Retrieval & Confidence Gating (Families 45-49)
    {
        "id": 45, "name": "critical_evidence_missing_cap",
        "clean": {"title": "Complete document evidence", "input": {"missing_critical": False}, "max_confidence": 100},
        "ambiguous": {"title": "Missing critical document fact caps at 59", "input": {"missing_critical": True}, "max_confidence": 59},
    },
    {
        "id": 46, "name": "canonical_ledger_fact_score",
        "clean": {"title": "Reconciled ledger cash query", "input": {"type": "canonical_ledger"}, "confidence": 100},
        "ambiguous": {"title": "Unreconciled draft estimate", "input": {"type": "draft_estimate"}, "confidence": 50},
    },
    {
        "id": 47, "name": "hybrid_rrf_priority_bonus",
        "clean": {"title": "Exact ID keyword and semantic match", "input": {"exact_id": "INV-9901", "semantic": "invoice payment"}, "top_rank": 1},
        "ambiguous": {"title": "Semantic similarity without exact ID", "input": {"exact_id": None, "semantic": "invoice payment"}, "top_rank": 2},
    },
    {
        "id": 48, "name": "agent_orchestration_budget_limit",
        "clean": {"title": "Simple query skips heavy specialist agents", "input": {"query_type": "factual"}, "agent_calls": 1},
        "ambiguous": {"title": "Complex reconciliation halts at budget max", "input": {"query_type": "complex_dispute", "max_budget": 8}, "agent_calls": 8},
    },
    {
        "id": 49, "name": "cross_tenant_evidence_isolation",
        "clean": {"title": "Tenant A queries own evidence", "input": {"tenant": "A", "query": "my documents"}, "matches_count": 1},
        "ambiguous": {"title": "Tenant B cannot retrieve Tenant A chunks", "input": {"tenant": "B", "query": "Tenant A documents"}, "matches_count": 0},
    },

    # Business Compliance & Statutory Governance (Families 50-54)
    {
        "id": 50, "name": "trade_license_annual_cutoff",
        "clean": {"title": "Trade license renewed before 30 September", "input": {"renewal_date": "2026-08-15"}, "is_expired": False},
        "ambiguous": {"title": "Trade license un-renewed past cutoff", "input": {"renewal_date": "2026-10-15"}, "is_expired": True},
    },
    {
        "id": 51, "name": "vat_turnover_threshold_rule",
        "clean": {"title": "Turnover < 50 Lakh BDT no mandatory VAT", "input": {"annual_turnover_paisa": 400000000}, "mandatory_vat": False},
        "ambiguous": {"title": "Turnover >= 50 Lakh BDT turnover tax applies", "input": {"annual_turnover_paisa": 600000000}, "mandatory_vat": True},
    },
    {
        "id": 52, "name": "income_tax_tin_and_return_deadline",
        "clean": {"title": "Tax return filed before 30 November", "input": {"filing_date": "2026-11-20"}, "compliant": True},
        "ambiguous": {"title": "Tax return past 30 November penalty risk", "input": {"filing_date": "2026-12-05"}, "compliant": False},
    },
    {
        "id": 53, "name": "out_of_scope_statutory_escalation",
        "clean": {"title": "MSME shop lease inquiry", "input": {"query": "দোকান ভাড়া চুক্তি বিধিমালা"}, "escalation_required": False},
        "ambiguous": {"title": "Criminal or boundary dispute inquiry", "input": {"query": "প্রতিবেশীর সাথে মারামারি ফৌজদারি মামলা"}, "escalation_required": True},
    },
    {
        "id": 54, "name": "no_hallucinated_legal_section",
        "clean": {"title": "Query mapped to verified statute", "input": {"query": "ভ্যাট আইন ২০১২"}, "citation_valid": True},
        "ambiguous": {"title": "Obscure query avoids invented section number", "input": {"query": "অজানা পৌর কর নিয়ম"}, "citation_valid": False, "escalation_required": True},
    },
]

cases = []
for f in families:
    f_id = f["id"]
    split = "development" if f_id <= 42 else "held_out"
    # Case A (Clean)
    cases.append({
        "id": f"CASE_{f_id}A",
        "family_id": f_id,
        "family_name": f["name"],
        "split": split,
        "title": f["clean"]["title"],
        "ambiguity_label": "clean",
        "input": f["clean"]["input"],
        "expected": f["clean"],
    })
    # Case B (Ambiguous / Boundary)
    cases.append({
        "id": f"CASE_{f_id}B",
        "family_id": f_id,
        "family_name": f["name"],
        "split": split,
        "title": f["ambiguous"]["title"],
        "ambiguity_label": "boundary_ambiguous",
        "input": f["ambiguous"]["input"],
        "expected": f["ambiguous"],
    })

benchmark = {
    "benchmark_name": "Shongoti Extension 30 Paired Families / 60 Cases Evaluation Benchmark",
    "version": "1.0.0",
    "created_at_utc": "2026-11-23T18:00:00Z",
    "total_story_families": len(families),
    "total_cases": len(cases),
    "splits": {
        "development": {"families": [f["id"] for f in families if f["id"] <= 42], "cases_count": 36},
        "held_out": {"families": [f["id"] for f in families if f["id"] > 42], "cases_count": 24},
    },
    "cases": cases,
}

out_path = os.path.join("tests", "fixtures", "evaluation", "extension_paired_benchmark.json")
with open(out_path, "w", encoding="utf-8") as fp:
    json.dump(benchmark, fp, indent=2, ensure_ascii=False)

print(f"Generated {len(cases)} cases across {len(families)} families into {out_path}")
