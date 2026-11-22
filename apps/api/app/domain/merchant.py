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
    def record_sale(
        cls,
        db: Session,
        tenant_id: str,
        sale_type: str,  # "cash", "credit", "split"
        total_amount_paisa: int,
        cash_received_paisa: int = 0,
        party_id: Optional[str] = None,
        items: Optional[List[Dict[str, int]]] = None,  # [{"product_id": str, "quantity": int}]
    ) -> JournalEntryModel:
        """
        Records a sale transaction atomically:
        - Creates balanced journal entry and postings
        - Updates account balances
        - If credit/split, increases customer due balance
        - If items provided, decrements product inventory
        """
        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        rec_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.RECEIVABLES.value, "Customer Dues", "asset")
        rev_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.SALES_REVENUE.value, "Sales Revenue", "revenue")

        entry_num = f"SL-{generate_uuid()[:8].upper()}"
        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=entry_num,
            description=f"{sale_type.title()} Sale",
        )
        db.add(entry)
        db.flush()

        postings = []

        if sale_type == "cash":
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="debit", amount_paisa=total_amount_paisa))
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=rev_acc.id, direction="credit", amount_paisa=total_amount_paisa))
            cash_acc.current_balance_paisa += total_amount_paisa
            rev_acc.current_balance_paisa += total_amount_paisa

        elif sale_type == "credit":
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=rec_acc.id, direction="debit", amount_paisa=total_amount_paisa))
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=rev_acc.id, direction="credit", amount_paisa=total_amount_paisa))
            rec_acc.current_balance_paisa += total_amount_paisa
            rev_acc.current_balance_paisa += total_amount_paisa
            if party_id:
                party = db.query(PartyModel).filter(PartyModel.id == party_id, PartyModel.tenant_id == tenant_id).first()
                if party:
                    party.current_due_paisa += total_amount_paisa

        elif sale_type == "split":
            receivable_paisa = total_amount_paisa - cash_received_paisa
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="debit", amount_paisa=cash_received_paisa))
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=rec_acc.id, direction="debit", amount_paisa=receivable_paisa))
            postings.append(PostingModel(journal_entry_id=entry.id, account_id=rev_acc.id, direction="credit", amount_paisa=total_amount_paisa))
            cash_acc.current_balance_paisa += cash_received_paisa
            rec_acc.current_balance_paisa += receivable_paisa
            rev_acc.current_balance_paisa += total_amount_paisa
            if party_id:
                party = db.query(PartyModel).filter(PartyModel.id == party_id, PartyModel.tenant_id == tenant_id).first()
                if party:
                    party.current_due_paisa += receivable_paisa

        for p in postings:
            db.add(p)

        # Inventory deduction
        if items:
            for item in items:
                prod = db.query(ProductItemModel).filter(ProductItemModel.id == item["product_id"], ProductItemModel.tenant_id == tenant_id).first()
                if prod:
                    prod.quantity_on_hand -= item["quantity"]
                    mov = StockMovementModel(
                        tenant_id=tenant_id,
                        product_id=prod.id,
                        movement_type="sale_deduction",
                        quantity_change=-item["quantity"],
                        reference_id=entry.id,
                    )
                    db.add(mov)

        db.commit()
        return entry

    @classmethod
    def record_debt_collection(
        cls, db: Session, tenant_id: str, party_id: str, amount_paisa: int
    ) -> JournalEntryModel:
        """
        Old-debt collection from customer:
        Debit Cash (+asset), Credit Receivables (-asset).
        Sales revenue change: 0. Customer due balance decreases.
        """
        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        rec_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.RECEIVABLES.value, "Customer Dues", "asset")

        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=f"COL-{generate_uuid()[:8].upper()}",
            description="Collect existing customer receivable",
        )
        db.add(entry)
        db.flush()

        p_cash = PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="debit", amount_paisa=amount_paisa)
        p_rec = PostingModel(journal_entry_id=entry.id, account_id=rec_acc.id, direction="credit", amount_paisa=amount_paisa)
        db.add(p_cash)
        db.add(p_rec)

        cash_acc.current_balance_paisa += amount_paisa
        rec_acc.current_balance_paisa -= amount_paisa

        party = db.query(PartyModel).filter(PartyModel.id == party_id, PartyModel.tenant_id == tenant_id).first()
        if party:
            party.current_due_paisa -= amount_paisa

        db.commit()
        return entry

    @classmethod
    def record_wallet_transfer(
        cls,
        db: Session,
        tenant_id: str,
        from_channel: str,  # e.g. "nagad"
        to_channel: str,    # e.g. "cash"
        principal_paisa: int,
        fee_paisa: int = 0,
    ) -> JournalEntryModel:
        """
        Transfer from digital wallet to cash drawer with fee.
        Debit Cash (principal), Debit TransferFee (fee), Credit DigitalWallet (principal + fee).
        """
        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        fee_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.TRANSFER_FEE.value, "Transfer Fee", "expense")
        wallet_acc = cls.get_or_create_account(db, tenant_id, f"asset:wallet:{from_channel}", f"{from_channel.title()} Wallet", "asset")

        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=f"TRF-{generate_uuid()[:8].upper()}",
            description=f"Transfer from {from_channel} to {to_channel}",
        )
        db.add(entry)
        db.flush()

        total_wallet_deduction = principal_paisa + fee_paisa
        p_cash = PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="debit", amount_paisa=principal_paisa)
        p_fee = PostingModel(journal_entry_id=entry.id, account_id=fee_acc.id, direction="debit", amount_paisa=fee_paisa) if fee_paisa > 0 else None
        p_wallet = PostingModel(journal_entry_id=entry.id, account_id=wallet_acc.id, direction="credit", amount_paisa=total_wallet_deduction)

        db.add(p_cash)
        if p_fee:
            db.add(p_fee)
        db.add(p_wallet)

        cash_acc.current_balance_paisa += principal_paisa
        fee_acc.current_balance_paisa += fee_paisa
        wallet_acc.current_balance_paisa -= total_wallet_deduction

        db.commit()
        return entry

    @classmethod
    def record_expense(
        cls, db: Session, tenant_id: str, amount_paisa: int, description: str, category: str = "operating"
    ) -> JournalEntryModel:
        """
        Record operating expense:
        Debit Operating Expense (+expense), Credit Cash (-asset).
        """
        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        exp_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.OPERATING_EXPENSE.value, "Operating Expense", "expense")

        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=f"EXP-{generate_uuid()[:8].upper()}",
            description=f"Expense: {description}",
        )
        db.add(entry)
        db.flush()

        p_exp = PostingModel(journal_entry_id=entry.id, account_id=exp_acc.id, direction="debit", amount_paisa=amount_paisa)
        p_cash = PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="credit", amount_paisa=amount_paisa)
        db.add(p_exp)
        db.add(p_cash)

        exp_acc.current_balance_paisa += amount_paisa
        cash_acc.current_balance_paisa -= amount_paisa

        db.commit()
        return entry

    @classmethod
    def record_owner_withdrawal(
        cls, db: Session, tenant_id: str, amount_paisa: int, user_role: str
    ) -> JournalEntryModel:
        """
        Record owner equity withdrawal:
        Cashier role is strictly forbidden from posting equity withdrawals.
        Debit Owner Draw (+equity draw), Credit Cash (-asset).
        Operating expense change: 0.
        """
        if user_role != "owner":
            raise PermissionError("Only shop owner is authorized to withdraw capital")

        cash_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.CASH.value, "Cash Drawer", "asset")
        draw_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.OWNER_DRAW.value, "Owner Drawings", "equity")

        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=f"DRW-{generate_uuid()[:8].upper()}",
            description="Owner capital withdrawal",
        )
        db.add(entry)
        db.flush()

        p_draw = PostingModel(journal_entry_id=entry.id, account_id=draw_acc.id, direction="debit", amount_paisa=amount_paisa)
        p_cash = PostingModel(journal_entry_id=entry.id, account_id=cash_acc.id, direction="credit", amount_paisa=amount_paisa)
        db.add(p_draw)
        db.add(p_cash)

        draw_acc.current_balance_paisa += amount_paisa
        cash_acc.current_balance_paisa -= amount_paisa

        db.commit()
        return entry

    @classmethod
    def record_supplier_payment(
        cls, db: Session, tenant_id: str, party_id: Optional[str], amount_paisa: int, channel: str = "cash"
    ) -> JournalEntryModel:
        """
        Supplier payment:
        Debit Accounts Payable / Supplier Obligations (-liability), Credit Cash/Wallet (-asset).
        Decrements supplier due balance if party provided.
        """
        pay_acc = cls.get_or_create_account(db, tenant_id, StandardAccount.PAYABLES.value, "Supplier Dues", "liability")
        credit_acc_code = StandardAccount.CASH.value if channel == "cash" else f"asset:wallet:{channel}"
        credit_acc_name = "Cash Drawer" if channel == "cash" else f"{channel.title()} Wallet"
        payment_source_acc = cls.get_or_create_account(db, tenant_id, credit_acc_code, credit_acc_name, "asset")

        entry = JournalEntryModel(
            tenant_id=tenant_id,
            entry_number=f"PAY-{generate_uuid()[:8].upper()}",
            description=f"Supplier payment via {channel}",
        )
        db.add(entry)
        db.flush()

        p_pay = PostingModel(journal_entry_id=entry.id, account_id=pay_acc.id, direction="debit", amount_paisa=amount_paisa)
        p_source = PostingModel(journal_entry_id=entry.id, account_id=payment_source_acc.id, direction="credit", amount_paisa=amount_paisa)
        db.add(p_pay)
        db.add(p_source)

        pay_acc.current_balance_paisa -= amount_paisa
        payment_source_acc.current_balance_paisa -= amount_paisa

        if party_id:
            party = db.query(PartyModel).filter(PartyModel.id == party_id, PartyModel.tenant_id == tenant_id).first()
            if party:
                party.current_due_paisa -= amount_paisa

        db.commit()
        return entry

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
