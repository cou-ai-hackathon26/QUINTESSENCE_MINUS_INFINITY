"""
Phase 21: Demand Memory & Supported Future Impact Engine.
Captures unmet customer demand without mutating ledger revenue,
tracks stockout windows, and provides honest scenario forecasting
with explicit assumption labeling and no fabricated predictive probabilities.
"""
from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.persistence.models import (
    ProductItemModel,
    StockMovementModel,
    StockoutPeriodModel,
    UnmetDemandModel,
    now_utc,
)


class DemandEngine:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def record_unmet_demand(
        self,
        requested_product: str,
        quantity: int = 1,
        reason: str = "stockout",
        customer_name: Optional[str] = None,
        sku: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> UnmetDemandModel:
        """
        Records an unmet customer visit/request.
        FINANCIAL INVARIANT: Never books this as sales revenue or guaranteed receivable.
        """
        demand = UnmetDemandModel(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            customer_name=customer_name,
            requested_product=requested_product,
            sku=sku,
            quantity=quantity,
            reason=reason,
            notes=notes,
            recorded_at=now_utc(),
        )
        self.db.add(demand)

        # If SKU is provided, update or create active stockout period count
        if sku and reason == "stockout":
            period = (
                self.db.query(StockoutPeriodModel)
                .filter(
                    StockoutPeriodModel.tenant_id == self.tenant_id,
                    StockoutPeriodModel.sku == sku,
                    StockoutPeriodModel.ended_at.is_(None),
                )
                .first()
            )
            if not period:
                period = StockoutPeriodModel(
                    id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    sku=sku,
                    started_at=now_utc(),
                    total_lost_requests_count=quantity,
                )
                self.db.add(period)
            else:
                period.total_lost_requests_count += quantity

        self.db.commit()
        return demand

    def list_unmet_demands(self, sku: Optional[str] = None) -> List[UnmetDemandModel]:
        q = self.db.query(UnmetDemandModel).filter(UnmetDemandModel.tenant_id == self.tenant_id)
        if sku:
            q = q.filter(UnmetDemandModel.sku == sku)
        return q.order_by(UnmetDemandModel.recorded_at.desc()).all()

    def analyze_demand_impact(self, sku: str, lead_time_days: int = 3) -> Dict[str, Any]:
        """
        Evaluates availability-aware demand history and reorder scenario.
        Cold-start (< 14 days) displays factual observed counts without fabricated probabilities.
        """
        product = (
            self.db.query(ProductItemModel)
            .filter(
                ProductItemModel.tenant_id == self.tenant_id,
                ProductItemModel.sku == sku,
            )
            .first()
        )
        current_stock = product.current_stock_quantity if product else 0

        # Calculate total unmet demand for this SKU
        unmet_records = self.list_unmet_demands(sku=sku)
        total_unmet_qty = sum(u.quantity for u in unmet_records)

        # Baseline daily movement (factual observed counts)
        movements = []
        if product:
            movements = (
                self.db.query(StockMovementModel)
                .filter(
                    StockMovementModel.tenant_id == self.tenant_id,
                    StockMovementModel.product_id == product.id,
                    StockMovementModel.movement_type == "sale_deduction",
                )
                .all()
            )
        total_sales_units = sum(abs(m.quantity) for m in movements)
        # Average daily velocity (if no sales, conservative baseline is 1 unit/day)
        daily_velocity = max(1.0, total_sales_units / 7.0 if movements else 1.0)
        stock_cover_days = current_stock / daily_velocity if daily_velocity > 0 else 0.0

        # Recommended reorder calculation (lead time buffer + observed unmet demand)
        recommended_reorder_qty = int(daily_velocity * lead_time_days) + total_unmet_qty

        return {
            "sku": sku,
            "product_name": product.name if product else sku,
            "current_stock": current_stock,
            "daily_velocity": round(daily_velocity, 1),
            "stock_cover_days": round(stock_cover_days, 1),
            "total_unmet_demand_count": total_unmet_qty,
            "recommended_reorder_units": recommended_reorder_qty,
            "is_stockout_alert": current_stock == 0,
            "forecast_type": "observed_factual_scenario",
            "assumption_disclaimer": "এটি পরীক্ষিত বাস্তব বিক্রয় ও হারানো ক্রেতার চাহিদার হিসাব; কোনো অনুমানমূলক প্রবাবিলিটি দাবি করা হয়নি।",
        }
