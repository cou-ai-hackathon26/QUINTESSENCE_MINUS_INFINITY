"""
Merchant Workflow Domain Engine.
Handles daily transactions, sales, debt collections, transfers, stock movements, and cash close.
One committed event atomically updates related accounts and registers.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.domain.ledger import PostingDirection, StandardAccount
from app.domain.money import Money
from app.persistence.models import (
    AccountModel,
    DailySnapshotModel,
    JournalEntryModel,
    PartyModel,
    PostingModel,
    ProductItemModel,
    StockMovementModel,
    generate_uuid,
    now_utc,
)


class MerchantService:
    @staticmethod
    def get_or_create_account(db: Session, tenant_id: str, code: str, name: str, acc_type: str) -> AccountModel:
        acc = db.query(AccountModel).filter(AccountModel.tenant_id == tenant_id, AccountModel.code == code).first()
        if not acc:
            acc = AccountModel(
                tenant_id=tenant_id,
                code=code,
                name=name,
                type=acc_type,
                current_balance_paisa=0,
            )
            db.add(acc)
            db.flush()
        return acc

    @classmethod
    def record_sale(cls,db,tenant_id,sale_type,total_amount_paisa,cash_received_paisa=0,party_id=None,items=None,request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'sale',{'sale_type':sale_type,'total_amount_paisa':total_amount_paisa,'cash_received_paisa':cash_received_paisa,'party_id':party_id,'items':items},request_key)

    @classmethod
    def record_debt_collection(cls,db,tenant_id,party_id,amount_paisa,request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'collection',{'party_id':party_id,'amount_paisa':amount_paisa},request_key)

    @classmethod
    def record_wallet_transfer(cls,db,tenant_id,from_channel,to_channel,principal_paisa,fee_paisa=0,request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'transfer',{'from_channel':from_channel,'to_channel':to_channel,'principal_paisa':principal_paisa,'fee_paisa':fee_paisa},request_key)

    @classmethod
    def record_expense(cls,db,tenant_id,amount_paisa,description,category='operating',request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'expense',{'amount_paisa':amount_paisa,'description':description,'category':category},request_key)

    @classmethod
    def record_owner_withdrawal(cls,db,tenant_id,amount_paisa,user_role,request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'withdrawal',{'amount_paisa':amount_paisa,'user_role':user_role},request_key)

    @classmethod
    def record_supplier_payment(cls,db,tenant_id,party_id,amount_paisa,channel='cash',request_key=None):
        from app.domain.merchant_posting import record
        return record(db,tenant_id,'supplier',{'party_id':party_id,'amount_paisa':amount_paisa,'channel':channel},request_key)

    @classmethod
    def record_cash_close(
        cls, db: Session, tenant_id: str, snapshot_date: str, actual_drawer_cash_paisa: int
    ) -> DailySnapshotModel:
        """
        Executes daily cash close:
        Compares ledger cash balance with physical drawer count, records discrepancy.
        """
        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        expected_cash = cash_acc.current_balance_paisa
        discrepancy = actual_drawer_cash_paisa - expected_cash

        snap = (
            db.query(DailySnapshotModel)
            .filter(
                DailySnapshotModel.tenant_id == tenant_id,
                DailySnapshotModel.snapshot_date == snapshot_date,
            )
            .first()
        )
        if not snap:
            snap = DailySnapshotModel(
                tenant_id=tenant_id,
                snapshot_date=snapshot_date,
                opening_cash_paisa=expected_cash,
            )
            db.add(snap)

        snap.closing_cash_paisa = expected_cash
        snap.actual_drawer_cash_paisa = actual_drawer_cash_paisa
        snap.discrepancy_paisa = discrepancy
        snap.status = "closed"
        snap.closed_at = now_utc()

        db.commit()
        return snap
