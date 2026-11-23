"""
Phase 20: Receiving, Returns, and Credit Recovery Engine.
Handles physical delivery intake, partial/short delivery detection,
usable inventory stock updates, credit note lifecycles, and
strictly exactly-once credit application to invoices.
"""
from __future__ import annotations
import uuid,json,hashlib
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.persistence.models import (
    CreditNoteModel,
    GoodsReceiptModel,
    PartyModel,
    ProductItemModel,
    StockMovementModel,
    AuditLogModel,EvidenceModel,ActionModel,
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
        request_key:Optional[str]=None,
    ) -> Dict[str, Any]:
        """
        Records delivery receipt.
        - Usable inventory stock is increased strictly by (received - damaged).
        - Discrepancies (shortage or damage) create a suspected CreditNoteModel.
        """
        if damaged_quantity>received_quantity:raise ValueError('Damaged quantity cannot exceed received quantity.')
        if purchase_draft_id and not self.db.query(ActionModel).filter_by(id=purchase_draft_id,tenant_id=self.tenant_id,action_type='stock_reorder').first():raise ValueError('Purchase draft not found in this shop.')
        audit=None
        if request_key:
            if len(request_key)>100:raise ValueError('Idempotency key exceeds 100 characters.')
            audit_id=str(uuid.uuid5(uuid.NAMESPACE_URL,self.tenant_id+'/receiving/'+request_key))
            fingerprint=hashlib.sha256(json.dumps({'supplier':supplier_name,'sku':sku,'ordered':ordered_quantity,'received':received_quantity,'damaged':damaged_quantity,'unit_price':unit_price_paisa,'draft':purchase_draft_id,'batch':batch_number,'expiry':expiry_date,'window':return_window_days},sort_keys=True).encode()).hexdigest()
            def existing():
                previous=self.db.query(AuditLogModel).filter_by(id=audit_id,tenant_id=self.tenant_id).first()
                if not previous:return None
                stored=json.loads(previous.details)
                if stored['fingerprint']!=fingerprint:raise ValueError('This idempotency key belongs to different delivery details.')
                return stored['response']
            replay=existing()
            if replay:return replay
            audit=AuditLogModel(id=audit_id,tenant_id=self.tenant_id,action='delivery_recorded',details='{}');self.db.add(audit)
            try:self.db.flush()
            except IntegrityError:
                self.db.rollback();replay=existing()
                if replay:return replay
                raise ValueError('A concurrent delivery changed; refresh before retrying.')
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
            .with_for_update().first()
        )
        if not product:
            self.db.rollback();raise ValueError('Create this SKU in Stock before receiving it. No stock or delivery was recorded.')
        if product:
            previous_quantity = product.quantity_on_hand
            product.quantity_on_hand += usable_quantity
            if usable_quantity and (product.cost_price_paisa is not None or previous_quantity == 0):
                total_cost = (product.cost_price_paisa or 0) * previous_quantity + unit_price_paisa * usable_quantity
                product.cost_price_paisa = (total_cost + product.quantity_on_hand // 2) // product.quantity_on_hand
            # Record stock movement
            movement = StockMovementModel(
                tenant_id=self.tenant_id,
                product_id=product.id,
                movement_type="purchase_addition",
                quantity_change=usable_quantity,
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

        response={
            "receipt_id": receipt.id,
            "status": receipt.status,
            "usable_quantity_added": usable_quantity,
            "shortage": shortage,
            "damaged": damaged_quantity,
            "credit_note_id": credit_note.id if credit_note else None,
            "claim_amount_bdt": (credit_note.amount_paisa / 100.0) if credit_note else 0.0,
        }
        if audit:audit.details=json.dumps({'fingerprint':fingerprint,'response':response})
        self.db.commit()
        return response

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

        if cn.status != "accepted_by_supplier":
            raise ValueError("Supplier acceptance must be established before applying this credit.")

        changed=self.db.query(CreditNoteModel).filter_by(id=cn.id,tenant_id=self.tenant_id,status='accepted_by_supplier').update({'status':'applied_to_bill','applied_invoice_ref':invoice_ref,'applied_at':now_utc()},synchronize_session=False)
        if changed!=1:self.db.rollback();raise ValueError('Credit state changed; refresh before applying it again.')
        self.db.commit()
        self.db.refresh(cn)

        return {
            "credit_note_id": cn.id,
            "status": cn.status,
            "applied_invoice_ref": cn.applied_invoice_ref,
            "amount_bdt": cn.amount_paisa / 100.0,
            "applied_at": cn.applied_at.isoformat() if cn.applied_at else None,
            "scope":"Owner-recorded application reference. No cash movement or automatic payable journal posting.",
        }

    def accept_credit(self,credit_note_id,source_evidence_id,user_id):
        note=self.db.query(CreditNoteModel).filter_by(id=credit_note_id,tenant_id=self.tenant_id).first()
        proof=self.db.query(EvidenceModel).filter_by(id=source_evidence_id,tenant_id=self.tenant_id).first()
        if not note or not proof:raise ValueError('Credit or original acceptance source not found in this shop.')
        if note.status=='applied_to_bill':raise ValueError('Applied credit cannot be reinterpreted.')
        if note.status=='accepted_by_supplier':return {'id':note.id,'status':note.status}
        changed=self.db.query(CreditNoteModel).filter_by(id=note.id,tenant_id=self.tenant_id,status=note.status).update({'status':'accepted_by_supplier'},synchronize_session=False)
        if changed!=1:self.db.rollback();raise ValueError('Credit changed; reopen its review.')
        self.db.add(AuditLogModel(tenant_id=self.tenant_id,user_id=user_id,action='supplier_credit_acceptance_reviewed',details=__import__('json').dumps({'credit_note_id':note.id,'source_evidence_id':proof.id,'source_sha256':proof.content_sha256,'amount_paisa':note.amount_paisa,'scope':'Owner verified explicit supplier acceptance; does not establish prior invoice deduction or spendable cash.'})))
        self.db.commit();return {'id':note.id,'status':'accepted_by_supplier','source_evidence_id':proof.id}
