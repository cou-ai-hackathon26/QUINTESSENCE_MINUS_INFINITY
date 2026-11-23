"""
Phase 19: Buying Desk Engine.
Handles supplier offer ingestion, bonus condition validation,
exact landed cost arithmetic (integer paisa), cash liquidity constraint feasibility,
and reviewable purchase order draft creation without unauthorized financial mutation.
"""
from __future__ import annotations
import json
import uuid
from decimal import Decimal,ROUND_HALF_UP
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.domain.ledger import StandardAccount
from app.persistence.models import (
    AccountModel,
    ActionModel,
    BuyingComparisonModel,
    SupplierOfferModel,
    now_utc,
)


class BuyingDeskEngine:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def ingest_offer(
        self,
        supplier_name: str,
        title: str,
        sku: str,
        base_unit_price_paisa: int,
        pack_size: int = 1,
        pack_unit: str = "পিস",
        min_order_quantity: int = 1,
        bonus_condition: Optional[Dict[str, Any]] = None,
        cash_discount_percent: float = 0.0,
        credit_period_days: int = 0,
        delivery_fee_paisa: int = 0,
        payment_method_required: str = "any",
        source_type: str = "manual",
        source_doc_id: Optional[str] = None,
    ) -> SupplierOfferModel:
        """
        Ingests supplier offer.
        If bonus condition exists (e.g. 10 cartons gives 1 free) but bonus SKU is unverified/unknown,
        score is capped at 59 (has_critical_blocker = True).
        """
        has_critical_blocker = False
        confidence_score = 90

        if bonus_condition:
            is_verified = bonus_condition.get("is_verified", False)
            bonus_sku = bonus_condition.get("bonus_sku")
            if not is_verified or bonus_sku!=sku or type(bonus_condition.get('buy_qty')) is not int or bonus_condition['buy_qty']<=0 or type(bonus_condition.get('bonus_qty')) is not int or bonus_condition['bonus_qty']<0:
                # Critical blocker: unconfirmed bonus eligibility or SKU
                has_critical_blocker = True
                confidence_score = 59
            else:
                confidence_score = 95

        offer = SupplierOfferModel(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            supplier_name=supplier_name,
            title=title,
            sku=sku,
            pack_size=pack_size,
            pack_unit=pack_unit,
            base_unit_price_paisa=base_unit_price_paisa,
            min_order_quantity=min_order_quantity,
            bonus_condition_json=json.dumps(bonus_condition) if bonus_condition else None,
            cash_discount_percent=cash_discount_percent,
            credit_period_days=credit_period_days,
            delivery_fee_paisa=delivery_fee_paisa,
            payment_method_required=payment_method_required,
            source_type=source_type,
            source_doc_id=source_doc_id,
            confidence_score=confidence_score,
            has_critical_blocker=has_critical_blocker,
            created_at=now_utc(),
        )
        self.db.add(offer)
        self.db.commit()
        return offer

    def list_offers(self, sku: Optional[str] = None) -> List[SupplierOfferModel]:
        q = self.db.query(SupplierOfferModel).filter(SupplierOfferModel.tenant_id == self.tenant_id)
        if sku:
            q = q.filter(SupplierOfferModel.sku == sku)
        return q.order_by(SupplierOfferModel.created_at.desc()).all()

    def compare_offers(self, target_sku: str, required_quantity: int) -> Dict[str, Any]:
        """
        Performs deterministic landed cost comparison across active supplier offers for target_sku:
        1. Landed total cost = (base_price * qty * (1 - discount)) + delivery_fee
        2. Effective received units = (qty + verified_bonus) * pack_size
        3. Effective unit cost (paisa) = total_cost // effective_units
        4. Evaluates cash liquidity constraint against current shop cash/wallet accounts.
        """
        offers = (
            self.db.query(SupplierOfferModel)
            .filter(
                SupplierOfferModel.tenant_id == self.tenant_id,
                SupplierOfferModel.sku == target_sku,
            )
            .all()
        )
        if not offers:
            raise ValueError(f"No supplier offers found for SKU: {target_sku}")

        # Check liquid cash availability
        cash_acc = (
            self.db.query(AccountModel)
            .filter(
                AccountModel.tenant_id == self.tenant_id,
                AccountModel.code == StandardAccount.CASH.value,
            )
            .first()
        )
        wallet_accounts = (
            self.db.query(AccountModel)
            .filter(
                AccountModel.tenant_id == self.tenant_id,
                AccountModel.code.in_([StandardAccount.MOBILE_BKASH.value, StandardAccount.MOBILE_NAGAD.value]),
            )
            .all()
        )
        liquid_cash_paisa = (cash_acc.current_balance_paisa if cash_acc else 0) + sum(account.current_balance_paisa for account in wallet_accounts)

        offer_evaluations = []
        overall_feasibility = "feasible_cash"

        for off in offers:
            meets_moq = required_quantity >= off.min_order_quantity

            # 1. Total Landed Cost Arithmetic
            gross_cost_paisa = off.base_unit_price_paisa * required_quantity
            discount_paisa = int((Decimal(gross_cost_paisa)*Decimal(str(off.cash_discount_percent))/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            subtotal_paisa = gross_cost_paisa - discount_paisa
            total_landed_paisa = subtotal_paisa + off.delivery_fee_paisa

            # 2. Bonus Condition Handling
            bonus_units = 0
            bonus_condition = json.loads(off.bonus_condition_json) if off.bonus_condition_json else None
            if bonus_condition and bonus_condition.get("is_verified") and bonus_condition.get('bonus_sku')==off.sku:
                buy_qty = bonus_condition.get("buy_qty", 10)
                bonus_qty = bonus_condition.get("bonus_qty", 1)
                if type(buy_qty) is int and buy_qty>0 and type(bonus_qty) is int and bonus_qty>=0:bonus_units = (required_quantity // buy_qty) * bonus_qty

            effective_units = (required_quantity + bonus_units) * off.pack_size
            effective_unit_cost_paisa = total_landed_paisa // effective_units if effective_units > 0 else total_landed_paisa

            # 3. Cash Constraint Feasibility
            is_cash_only = off.payment_method_required == "cash" or off.credit_period_days == 0
            capacity=(cash_acc.current_balance_paisa if cash_acc else 0) if off.payment_method_required=='cash' else next((a.current_balance_paisa for a in wallet_accounts if a.code=='asset:wallet:'+off.payment_method_required),0) if off.payment_method_required in ('bkash','nagad') else liquid_cash_paisa
            has_sufficient_cash = capacity >= total_landed_paisa

            if is_cash_only and not has_sufficient_cash:
                feasibility = "infeasible_insufficient_cash"
                shortfall_paisa = total_landed_paisa - capacity
            elif has_sufficient_cash:
                feasibility = "feasible_cash"
                shortfall_paisa = 0
            else:
                feasibility = "feasible_credit"
                shortfall_paisa = 0

            offer_evaluations.append({
                "offer_id": off.id,
                "supplier_name": off.supplier_name,
                "title": off.title,
                "base_unit_price_bdt": off.base_unit_price_paisa / 100.0,
                "total_landed_cost_bdt": total_landed_paisa / 100.0,
                "effective_unit_cost_bdt": effective_unit_cost_paisa / 100.0,
                "effective_unit_cost_paisa": effective_unit_cost_paisa,
                "bonus_units_awarded": bonus_units,
                "meets_moq": meets_moq,
                "feasibility": feasibility,
                "shortfall_bdt": shortfall_paisa / 100.0,
                "confidence_score": off.confidence_score,
                "has_critical_blocker": off.has_critical_blocker,
                "credit_period_days": off.credit_period_days,
            })

        # Rank offers: prioritize feasible offers, then lowest effective unit cost
        eligible_offers=[o for o in offer_evaluations if o['meets_moq'] and not o['has_critical_blocker']]
        feasible_offers = [o for o in eligible_offers if o["feasibility"] != "infeasible_insufficient_cash"]
        if feasible_offers:
            feasible_offers.sort(key=lambda x: x["effective_unit_cost_paisa"])
            best_offer = feasible_offers[0]
            overall_feasibility = best_offer["feasibility"]
        else:
            offer_evaluations.sort(key=lambda x: x["effective_unit_cost_paisa"])
            best_offer = offer_evaluations[0]
            overall_feasibility = "infeasible_insufficient_cash"

        comparison = BuyingComparisonModel(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            target_sku=target_sku,
            required_quantity=required_quantity,
            best_offer_id=best_offer["offer_id"],
            comparison_summary_json=json.dumps({
                "available_liquid_cash_bdt": liquid_cash_paisa / 100.0,
                "offers": offer_evaluations,
            }),
            feasibility_status=overall_feasibility,
            created_at=now_utc(),
        )
        self.db.add(comparison)
        self.db.commit()

        return {
            "comparison_id": comparison.id,
            "target_sku": target_sku,
            "required_quantity": required_quantity,
            "available_liquid_cash_bdt": liquid_cash_paisa / 100.0,
            "best_offer_id": best_offer["offer_id"],
            "best_supplier": best_offer["supplier_name"],
            "best_effective_unit_cost_bdt": best_offer["effective_unit_cost_bdt"],
            "feasibility_status": overall_feasibility,
            "evaluations": offer_evaluations,
        }

    def create_order_draft(
        self,
        comparison_id: str,
        offer_id: str,
        quantity: int,
        user_id: Optional[str] = None,
    ) -> ActionModel:
        """
        Creates a purchase order draft.
        Never executes automatic payment or direct ledger postings;
        returns draft action requiring explicit owner review and approval.
        """
        offer = (
            self.db.query(SupplierOfferModel)
            .filter(
                SupplierOfferModel.id == offer_id,
                SupplierOfferModel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if not offer:
            raise ValueError("Offer not found or unauthorized")

        comparison=self.db.query(BuyingComparisonModel).filter_by(id=comparison_id,tenant_id=self.tenant_id).first()
        if not comparison or comparison.target_sku!=offer.sku or comparison.required_quantity!=quantity:raise ValueError('Comparison is missing, belongs to another shop/SKU or uses a different quantity. Compare again.')
        if quantity<offer.min_order_quantity:raise ValueError('Quantity is below the supplier minimum order.')
        if offer.has_critical_blocker:raise ValueError('Resolve critical offer terms before preparing this order.')
        if offer.id not in {row['offer_id'] for row in json.loads(comparison.comparison_summary_json)['offers']}:raise ValueError('Offer was not part of this comparison.')

        gross_paisa = offer.base_unit_price_paisa * quantity
        discount_paisa = int((Decimal(gross_paisa)*Decimal(str(offer.cash_discount_percent))/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        total_paisa = gross_paisa - discount_paisa + offer.delivery_fee_paisa

        action_draft = ActionModel(
            tenant_id=self.tenant_id,
            action_type="stock_reorder",
            recipient=offer.supplier_name,
            amount_paisa=total_paisa,
            status="draft",
            payload_json=json.dumps({
                "comparison_id": comparison_id,
                "offer_id": offer.id,
                "sku": offer.sku,
                "quantity": quantity,
                "pack_size": offer.pack_size,
                "amount_bdt": total_paisa / 100.0,
            }),
            created_by_user_id=user_id,
            created_at=now_utc(),
        )
        self.db.add(action_draft)
        self.db.commit()
        return action_draft
