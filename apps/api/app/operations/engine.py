"""Phase 23: Everyday Operations Engine

Implements customer reservations/picking drafts, shift handover reconciliation with factual
hypotheses, scoped supplier change impact, and returnable container deposit tracking.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.persistence.models import (
    CustomerReservationModel,
    ReturnableContainerModel,
    ShiftHandoverModel,
    ProductItemModel,
    CreditNoteModel,
    GoodsReceiptModel,
)


class EverydayOperationsEngine:
    """Manages everyday store operations preserving all financial & inventory invariants."""

    @staticmethod
    def create_reservation(
        db: Session,
        tenant_id: str,
        customer_name: Optional[str],
        customer_phone: Optional[str],
        items: List[Dict[str, Any]],
        deposit_paisa: int = 0,
        expiry_hours: int = 24,
    ) -> CustomerReservationModel:
        """
        Creates customer order reservation with availability checking and picking guidance.
        Financial Invariant: A customer reservation NEVER creates revenue, receivables,
        or ledger entries.
        """
        total_paisa = 0
        enriched_items = []

        for it in items:
            sku = it.get("sku", "").strip()
            qty = int(it.get("quantity", 1))
            unit_price = int(it.get("unit_price_paisa", 0))
            name = it.get("name", sku)

            # Check product stock availability
            product = db.query(ProductItemModel).filter(
                ProductItemModel.tenant_id == tenant_id,
                ProductItemModel.sku == sku,
            ).first()

            available_stock = product.quantity_on_hand if product else 0
            pick_status = "ready" if available_stock >= qty else "needs_substitution"

            total_paisa += unit_price * qty
            enriched_items.append({
                "sku": sku,
                "name": name,
                "quantity": qty,
                "unit_price_paisa": unit_price,
                "available_stock": available_stock,
                "pick_status": pick_status,
            })

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiry_hours)

        reservation = CustomerReservationModel(
            tenant_id=tenant_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            items_json=json.dumps(enriched_items, ensure_ascii=False),
            status="reserved",
            total_estimated_paisa=total_paisa,
            deposit_paisa=deposit_paisa,
            expires_at=expires_at,
            created_at=now,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    @staticmethod
    def pick_reservation(db: Session, tenant_id: str, reservation_id: str) -> CustomerReservationModel:
        """Marks reserved items as physically picked and packed for customer pickup."""
        res = db.query(CustomerReservationModel).filter(
            CustomerReservationModel.id == reservation_id,
            CustomerReservationModel.tenant_id == tenant_id,
        ).first()
        if not res:
            raise ValueError(f"Reservation {reservation_id} not found")
        if res.status != "reserved":
            raise ValueError(f"Cannot pick reservation in status '{res.status}'")

        res.status = "picked"
        db.commit()
        db.refresh(res)
        return res

    @staticmethod
    def expire_stale_reservations(db: Session, tenant_id: str) -> int:
        """Deterministically expires past-due reservations without penalty."""
        now = datetime.now(timezone.utc)
        stale = db.query(CustomerReservationModel).filter(
            CustomerReservationModel.tenant_id == tenant_id,
            CustomerReservationModel.status == "reserved",
            CustomerReservationModel.expires_at < now,
        ).all()

        for s in stale:
            s.status = "expired"
        db.commit()
        return len(stale)

    @staticmethod
    def record_container_movement(
        db: Session,
        tenant_id: str,
        container_type: str,
        party_name: str,
        count: int,
        movement_type: str,  # 'issue' or 'return'
        deposit_per_unit_paisa: int = 0,
        party_id: Optional[str] = None,
    ) -> ReturnableContainerModel:
        """
        Tracks returnable containers (crates, bottles) and refundable deposits.
        Financial Invariant: Container deposit tracking is strictly separated from goods sales revenue.
        """
        container = db.query(ReturnableContainerModel).filter(
            ReturnableContainerModel.tenant_id == tenant_id,
            ReturnableContainerModel.container_type == container_type,
            ReturnableContainerModel.party_name == party_name,
        ).first()

        now = datetime.now(timezone.utc)
        if not container:
            container = ReturnableContainerModel(
                tenant_id=tenant_id,
                container_type=container_type,
                party_id=party_id,
                party_name=party_name,
                issued_count=0,
                returned_count=0,
                outstanding_count=0,
                deposit_per_unit_paisa=deposit_per_unit_paisa,
                total_deposit_held_paisa=0,
                created_at=now,
                updated_at=now,
            )
            db.add(container)

        if movement_type == "issue":
            container.issued_count += count
            container.outstanding_count += count
            if deposit_per_unit_paisa > 0:
                container.deposit_per_unit_paisa = deposit_per_unit_paisa
            container.total_deposit_held_paisa += count * container.deposit_per_unit_paisa
        elif movement_type == "return":
            container.returned_count += count
            container.outstanding_count = max(0, container.outstanding_count - count)
            container.total_deposit_held_paisa = max(
                0, container.total_deposit_held_paisa - (count * container.deposit_per_unit_paisa)
            )
        else:
            raise ValueError(f"Invalid movement_type: '{movement_type}'")

        container.updated_at = now
        db.commit()
        db.refresh(container)
        return container

    @staticmethod
    def create_shift_handover(
        db: Session,
        tenant_id: str,
        shift_name: str,
        opened_by: str,
        closed_by: str,
        declared_cash_paisa: int,
        system_cash_paisa: int,
        notes: Optional[str] = None,
    ) -> ShiftHandoverModel:
        """
        Creates evidence-linked shift handover. Inspects operational records to formulate
        factual hypotheses for cash variances without accusatory claims.
        """
        variance = declared_cash_paisa - system_cash_paisa
        hypotheses = []

        if variance != 0:
            # Check for unapplied credits or pending receipts
            recent_receipts = db.query(GoodsReceiptModel).filter(
                GoodsReceiptModel.tenant_id == tenant_id,
                GoodsReceiptModel.status == "discrepant",
            ).limit(3).all()

            for r in recent_receipts:
                hypotheses.append({
                    "hypothesis": f"Supplier delivery discrepancy on {r.sku} ({r.shortage_quantity} units shortage)",
                    "source": f"receipt:{r.id}",
                    "confidence_score": 75,
                })

            unapplied_credits = db.query(CreditNoteModel).filter(
                CreditNoteModel.tenant_id == tenant_id,
                CreditNoteModel.status == "accepted_by_supplier",
            ).limit(3).all()

            for c in unapplied_credits:
                hypotheses.append({
                    "hypothesis": f"Unapplied supplier credit note of ৳{c.amount_paisa / 100:.2f} from {c.supplier_name}",
                    "source": f"credit_note:{c.id}",
                    "confidence_score": 80,
                })

            if not hypotheses:
                hypotheses.append({
                    "hypothesis": "Unrecorded small cash expense, change discrepancy, or pending customer receipt",
                    "source": "operational_variance",
                    "confidence_score": 50,
                })

        now = datetime.now(timezone.utc)
        handover = ShiftHandoverModel(
            tenant_id=tenant_id,
            shift_name=shift_name,
            opened_by=opened_by,
            closed_by=closed_by,
            declared_cash_paisa=declared_cash_paisa,
            system_cash_paisa=system_cash_paisa,
            variance_paisa=variance,
            notes=notes,
            possible_reasons_json=json.dumps(hypotheses, ensure_ascii=False) if hypotheses else None,
            created_at=now,
        )
        db.add(handover)
        db.commit()
        db.refresh(handover)
        return handover

    @staticmethod
    def evaluate_supplier_change_proposal(
        tenant_id: str,
        supplier_name: str,
        target_order_id: str,
        sku: str,
        original_price_paisa: int,
        proposed_price_paisa: int,
        quantity: int,
        proposed_delay_days: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluates scoped supplier delivery/price change proposal.
        Strict invariant: A proposal scoped to a specific order must NOT rewrite future orders globally.
        """
        price_diff = proposed_price_paisa - original_price_paisa
        total_impact_paisa = price_diff * quantity

        margin_impact = "favorable" if price_diff < 0 else ("unfavorable" if price_diff > 0 else "neutral")
        advice = (
            f"Supplier {supplier_name} proposed a price change of ৳{price_diff / 100:+.2f} per unit for order {target_order_id}. "
            f"Total financial impact: ৳{total_impact_paisa / 100:+.2f}. "
            f"Delivery delay: {proposed_delay_days} days. Scoped strictly to this order."
        )

        return {
            "tenant_id": tenant_id,
            "target_order_id": target_order_id,
            "supplier_name": supplier_name,
            "sku": sku,
            "quantity": quantity,
            "original_price_paisa": original_price_paisa,
            "proposed_price_paisa": proposed_price_paisa,
            "price_diff_per_unit_paisa": price_diff,
            "total_impact_paisa": total_impact_paisa,
            "proposed_delay_days": proposed_delay_days,
            "margin_impact": margin_impact,
            "review_required": True,
            "scope": "scoped_to_order_only",
            "advisory_bn": f"{supplier_name}-এর প্রস্তাবিত পরিবর্তনটি কেবল {target_order_id} অর্ডারের জন্য প্রযোজ্য। মোট প্রভাব: ৳{total_impact_paisa / 100:.2f}।",
            "advisory_en": advice,
        }
