"""
Strict Claim Schemas with Explicit Null / Unknown Handling.
A model parse never authorizes ledger writes or sets defaults on failure.
"""
from typing import Optional
from pydantic import BaseModel, Field


class StructuredClaimExtraction(BaseModel):
    party_name: Optional[str] = Field(None, description="Identified merchant/supplier name or None if unknown")
    invoice_ref: Optional[str] = Field(None, description="Invoice/memo number or None if unknown")
    amount_paisa: Optional[int] = Field(None, description="Exact integer paisa or None if illegible/absent")
    claim_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format or None")
    payment_method: Optional[str] = Field(None, description="Identified method (cash, bkash, nagad, bank) or None")
    confidence: Optional[float] = Field(None, description="Model self-reported confidence score")
    raw_snippet: Optional[str] = Field(None, description="Original source text snippet")
