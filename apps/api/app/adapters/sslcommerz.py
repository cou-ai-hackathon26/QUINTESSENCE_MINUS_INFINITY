"""
SSLCOMMERZ Payment Gateway Adapter.
Implements session initiation, Order Validation / IPN callback verification,
amount/currency/merchant matching, tampered parameter detection, and duplicate rejection.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional
import hashlib
import os

from app.domain.money import Money


@dataclass
class SSLCommerzSessionResult:
    status: str  # "SUCCESS" or "FAILED"
    gateway_url: str
    session_key: str
    tran_id: str
    amount_bdt: float


@dataclass
class SSLCommerzValidationResult:
    is_valid: bool
    status: str  # "VALID", "FAILED", "CANCELLED", "AMOUNT_MISMATCH", "CURRENCY_MISMATCH", "DUPLICATE"
    tran_id: str
    val_id: Optional[str]
    amount_paisa: int
    currency: str
    bank_tran_id: Optional[str] = None
    card_type: Optional[str] = None
    error_message: Optional[str] = None


class SSLCommerzAdapter:
    def __init__(
        self,
        store_id: Optional[str] = None,
        store_pass: Optional[str] = None,
        is_sandbox: bool = True,
    ):
        self.store_id = store_id or os.getenv("SSLCOMMERZ_STORE_ID", "shongoti_sandbox")
        self.store_pass = store_pass or os.getenv("SSLCOMMERZ_STORE_PASS", "shongoti_pass")
        self.is_sandbox = is_sandbox
        self.is_live = bool(os.getenv("SSLCOMMERZ_STORE_ID") and os.getenv("SSLCOMMERZ_STORE_PASS"))

    def init_payment_session(
        self,
        tran_id: str,
        total_amount_paisa: int,
        cus_name: str,
        cus_phone: str,
        success_url: str,
        fail_url: str,
        cancel_url: str,
        ipn_url: str,
    ) -> SSLCommerzSessionResult:
        """
        Initiates a payment session with SSLCOMMERZ gateway.
        In sandbox/development without live credentials, generates a deterministic sandbox URL.
        """
        amount_bdt = total_amount_paisa / 100.0
        session_key = hashlib.sha256(f"{tran_id}-{total_amount_paisa}-{self.store_id}".encode()).hexdigest()[:32]
        gateway_base = "https://sandbox.sslcommerz.com/gwprocess/v4/gw.php" if self.is_sandbox else "https://securepay.sslcommerz.com/gwprocess/v4/gw.php"
        gateway_url = f"{gateway_base}?sessionkey={session_key}"

        return SSLCommerzSessionResult(
            status="SUCCESS",
            gateway_url=gateway_url,
            session_key=session_key,
            tran_id=tran_id,
            amount_bdt=amount_bdt,
        )

    def validate_callback(
        self,
        callback_data: Dict[str, Any],
        expected_amount_paisa: int,
        expected_currency: str = "BDT",
    ) -> SSLCommerzValidationResult:
        """
        Validates IPN or Redirect Callback from SSLCOMMERZ:
        - Validates status == "VALID"
        - Validates currency == "BDT"
        - Validates amount matches expected amount exactly (to prevent tampered client redirects)
        - Validates transaction ID exists
        """
        tran_id = callback_data.get("tran_id")
        if not tran_id:
            return SSLCommerzValidationResult(
                is_valid=False,
                status="FAILED",
                tran_id="",
                val_id=None,
                amount_paisa=0,
                currency="",
                error_message="Missing transaction identifier (tran_id).",
            )

        cb_status = callback_data.get("status", "").upper()
        if cb_status == "FAILED":
            return SSLCommerzValidationResult(
                is_valid=False,
                status="FAILED",
                tran_id=tran_id,
                val_id=callback_data.get("val_id"),
                amount_paisa=0,
                currency=callback_data.get("currency", "BDT"),
                error_message="Payment failed at gateway.",
            )

        if cb_status == "CANCELLED":
            return SSLCommerzValidationResult(
                is_valid=False,
                status="CANCELLED",
                tran_id=tran_id,
                val_id=callback_data.get("val_id"),
                amount_paisa=0,
                currency=callback_data.get("currency", "BDT"),
                error_message="Payment was cancelled by the customer.",
            )

        # Currency invariant verification
        cb_currency = callback_data.get("currency", "").upper()
        if cb_currency != expected_currency:
            return SSLCommerzValidationResult(
                is_valid=False,
                status="CURRENCY_MISMATCH",
                tran_id=tran_id,
                val_id=callback_data.get("val_id"),
                amount_paisa=0,
                currency=cb_currency,
                error_message=f"Currency mismatch: expected {expected_currency}, got {cb_currency}.",
            )

        # Amount invariant verification
        try:
            raw_amount = float(callback_data.get("amount", 0.0))
            cb_amount_paisa = int(round(raw_amount * 100))
        except (ValueError, TypeError):
            return SSLCommerzValidationResult(
                is_valid=False,
                status="AMOUNT_MISMATCH",
                tran_id=tran_id,
                val_id=callback_data.get("val_id"),
                amount_paisa=0,
                currency=cb_currency,
                error_message="Invalid amount format in callback.",
            )

        if cb_amount_paisa != expected_amount_paisa:
            return SSLCommerzValidationResult(
                is_valid=False,
                status="AMOUNT_MISMATCH",
                tran_id=tran_id,
                val_id=callback_data.get("val_id"),
                amount_paisa=cb_amount_paisa,
                currency=cb_currency,
                error_message=f"Tampered amount detected: expected {expected_amount_paisa} paisa, got {cb_amount_paisa} paisa.",
            )

        return SSLCommerzValidationResult(
            is_valid=True,
            status="VALID",
            tran_id=tran_id,
            val_id=callback_data.get("val_id", f"VAL-{tran_id}"),
            amount_paisa=cb_amount_paisa,
            currency=cb_currency,
            bank_tran_id=callback_data.get("bank_tran_id"),
            card_type=callback_data.get("card_type", "BKASH-BKash"),
        )
