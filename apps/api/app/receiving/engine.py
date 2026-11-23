"""
Phase 20: Receiving, Returns, and Credit Recovery Engine.
Handles physical delivery intake, partial/short delivery detection,
usable inventory stock updates, credit note lifecycles, and
strictly exactly-once credit application to invoices.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.persistence.models import (
    CreditNoteModel,
    GoodsReceiptModel,
    PartyModel,
    ProductItemModel,
    StockMovementModel,
    now_utc,
)


class ReceivingEngine:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def record_receipt(
        self,
        supplier_name: str,
        sku: str,
        ordered_quantity: int,
        received_quantity: int,
        damaged_quantity: int = 0,
        unit_price_paisa: int = 10000,
        purchase_draft_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        expiry_date: Optional[str] = None,
        return_window_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Records delivery receipt.
        - Usable inventory stock is increased strictly by (received - damaged).
        - Discrepancies (shortage or damage) create a suspected CreditNoteModel.
        """
        shortage = max(0, ordered_quantity - received_quantity)
        usable_quantity = max(0, received_quantity - damaged_quantity)

        status = "complete"
        if shortage > 0 or damaged_quantity > 0:
            status = "discrepant" if received_quantity > 0 else "partial"

        receipt = GoodsReceiptModel(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            purchase_draft_id=purchase_draft_id,
            supplier_name=supplier_name,
            sku=sku,
            ordered_quantity=ordered_quantity,
            received_quantity=received_quantity,
            damaged_quantity=damaged_quantity,
            shortage_quantity=shortage,
            batch_number=batch_number,
            expiry_date=expiry_date,
            status=status,
            created_at=now_utc(),
        )
        self.db.add(receipt)
        self.db.flush()

        # Update physical stock for usable units
        product = (
            self.db.query(ProductItemModel)
            .filter(
                ProductItemModel.tenant_id == self.tenant_id,
                ProductItemModel.sku == sku,
            )
            .first()
        )
        if product:
            product.current_stock_quantity += usable_quantity
            # Record stock movement
            movement = StockMovementModel(
                tenant_id=self.tenant_id,
                product_id=product.id,
                movement_type="purchase_receive",
                quantity=usable_quantity,
                reference_id=receipt.id,
            )
            self.db.add(movement)

        # Create suspected credit note if there is shortage or damage
        credit_note = None
        discrepant_units = shortage + damaged_quantity
        if discrepant_units > 0:
            claim_amount = discrepant_units * unit_price_paisa
            deadline = datetime.now(timezone.utc) + timedelta(days=return_window_days)
            claim_reason = "damaged" if damaged_quantity > 0 and shortage == 0 else "shortage" if shortage > 0 and damaged_quantity == 0 else "shortage_and_damaged"

            credit_note = CreditNoteModel(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                receipt_id=receipt.id,
                supplier_name=supplier_name,
                claim_reason=claim_reason,
                amount_paisa=claim_amount,
                status="suspected",
                return_window_deadline=deadline,
                created_at=now_utc(),
            )
            self.db.add(credit_note)

        self.db.commit()

        return {
            "receipt_id": receipt.id,
            "status": receipt.status,
            "usable_quantity_added": usable_quantity,
            "shortage": shortage,
            "damaged": damaged_quantity,
            "credit_note_id": credit_note.id if credit_note else None,
            "claim_amount_bdt": (credit_note.amount_paisa / 100.0) if credit_note else 0.0,
        }

    def list_receipts(self) -> List[GoodsReceiptModel]:
        return (
            self.db.query(GoodsReceiptModel)
            .filter(GoodsReceiptModel.tenant_id == self.tenant_id)
            .order_by(GoodsReceiptModel.created_at.desc())
            .all()
        )

    def list_credit_notes(self) -> List[CreditNoteModel]:
        return (
            self.db.query(CreditNoteModel)
            .filter(CreditNoteModel.tenant_id == self.tenant_id)
            .order_by(CreditNoteModel.created_at.desc())
            .all()
        )

    def apply_credit_to_invoice(self, credit_note_id: str, invoice_ref: str) -> Dict[str, Any]:
        """
        Applies an agreed credit note to a bill or future invoice.
        Enforces strictly exactly-once application invariant;
        attempting to apply an already applied credit note raises ValueError.
        """
        cn = (
            self.db.query(CreditNoteModel)
            .filter(
                CreditNoteModel.id == credit_note_id,
                CreditNoteModel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if not cn:
            raise ValueError("Credit note not found or unauthorized")

        if cn.status == "applied_to_bill":
            raise ValueError(f"Credit note {credit_note_id} has already been applied to invoice {cn.applied_invoice_ref}. Duplicate credit application is prohibited.")

        cn.status = "applied_to_bill"
        cn.applied_invoice_ref = invoice_ref
        cn.applied_at = now_utc()
        self.db.commit()

        return {
            "credit_note_id": cn.id,
            "status": cn.status,
            "applied_invoice_ref": cn.applied_invoice_ref,
            "amount_bdt": cn.amount_paisa / 100.0,
            "applied_at": cn.applied_at.isoformat() if cn.applied_at else None,
        }
