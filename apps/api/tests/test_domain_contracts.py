"""
Domain Contract Fixtures Verification
Verifies that all synthetic golden contracts provided in Phase 00
are well-formed, adhere to schema, and contain non-empty test cases.
"""
import json
import os
import pytest

FIXTURES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests", "fixtures", "contracts")
)


def load_fixture(filename: str) -> dict:
    filepath = os.path.join(FIXTURES_DIR, filename)
    assert os.path.exists(filepath), f"Contract fixture missing: {filepath}"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def test_reconciliation_contract_fixture():
    data = load_fixture("reconciliation.json")
    assert data["synthetic"] is True
    assert data["currency"] == "BDT"
    assert data["money_unit"] == "paisa"
    assert "source_facts" in data
    assert len(data["cases"]) == 8
    
    # Verify demand is 2500000 paisa (BDT 25,000)
    assert data["source_facts"]["demand"]["amount"] == 2500000


def test_posting_contract_fixture():
    data = load_fixture("posting.json")
    assert data["synthetic"] is True
    assert data["currency"] == "BDT"
    assert data["money_unit"] == "paisa"
    assert len(data["cases"]) >= 8


def test_liquidity_contract_fixture():
    data = load_fixture("liquidity.json")
    assert data["synthetic"] is True
    assert data["currency"] == "BDT"
    assert "accounts" in data
    assert len(data["cases"]) >= 6


def test_cash_scenarios_contract_fixture():
    data = load_fixture("cash-scenarios.json")
    assert data["synthetic"] is True
    assert data["currency"] == "BDT"
    assert len(data["dates"]) == 7
    assert len(data["cases"]) >= 4
