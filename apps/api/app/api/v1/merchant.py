"""
Merchant Workflow API Router.
Exposes daily sales, debt collections, transfers, stock tracking, and today's summary.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field,StrictInt
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.domain.merchant import MerchantService
from app.domain.ledger import StandardAccount
from app.persistence.models import (
    AccountModel,
    DailySnapshotModel,
    PartyModel,
    ProductItemModel,
    UserModel,
    now_utc,
    JournalEntryModel,PostingModel,
)

merchant_router = APIRouter(prefix="/api/v1/merchant", tags=["Merchant Workflow"])


# --- DTOs ---

class SaleItemDTO(BaseModel):
    product_id: str
    quantity: StrictInt = Field(..., gt=0)


class SaleRequestDTO(BaseModel):
    sale_type: str = Field(..., pattern="^(cash|credit|split)$")
    total_amount_paisa: StrictInt = Field(..., gt=0)
    cash_received_paisa: StrictInt = Field(0, ge=0)
    party_id: Optional[str] = None
    items: Optional[List[SaleItemDTO]] = None


class DebtCollectionDTO(BaseModel):
    party_id: str
    amount_paisa: StrictInt = Field(..., gt=0)


class TransferDTO(BaseModel):
    from_channel: str
    to_channel: str = "cash"
    principal_paisa: StrictInt = Field(..., gt=0)
    fee_paisa: StrictInt = Field(0, ge=0)


class CashCloseDTO(BaseModel):
    snapshot_date: str  # YYYY-MM-DD
    actual_drawer_cash_paisa: StrictInt = Field(..., ge=0)


class ExpenseCreateDTO(BaseModel):
    amount_paisa: StrictInt = Field(..., gt=0)
    description: str
    category: str = "operating"


class WithdrawalCreateDTO(BaseModel):
    amount_paisa: StrictInt = Field(..., gt=0)


class SupplierPaymentDTO(BaseModel):
    party_id: Optional[str] = None
    amount_paisa: StrictInt = Field(..., gt=0)
    channel: str = "cash"


class PartyCreateDTO(BaseModel):
    name: str
    phone: Optional[str] = None
    party_type: str = Field('customer',pattern='^(customer|supplier)$')
    initial_due_paisa: StrictInt = Field(0, ge=0)


class ProductCreateDTO(BaseModel):
    name: str
    sku: Optional[str] = None
    unit: str = "pcs"
    quantity_on_hand: StrictInt = Field(0, ge=0)
    cost_price_paisa: Optional[int] = Field(None, ge=0)
    selling_price_paisa: StrictInt = Field(..., ge=0)


# --- Endpoints ---

@merchant_router.get("/today")
def get_today_summary(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Derives today's financial summary directly from the single ledger truth.
    """
    cash_acc = db.query(AccountModel).filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code == StandardAccount.CASH.value).first()
    rec_acc = db.query(AccountModel).filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code == StandardAccount.RECEIVABLES.value).first()
    pay_acc = db.query(AccountModel).filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code == StandardAccount.PAYABLES.value).first()
    rev_acc = db.query(AccountModel).filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code == StandardAccount.SALES_REVENUE.value).first()
    exp_acc = db.query(AccountModel).filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code == StandardAccount.OPERATING_EXPENSE.value).first()

    digital_accounts = (
        db.query(AccountModel)
        .filter(AccountModel.tenant_id == current_user.tenant_id, AccountModel.code.like("asset:wallet:%"))
        .all()
    )
    digital_total = sum(acc.current_balance_paisa for acc in digital_accounts)

    return {
        "cash_balance_paisa": cash_acc.current_balance_paisa if cash_acc else 0,
        "digital_wallet_balance_paisa": digital_total,
        "customer_dues_paisa": rec_acc.current_balance_paisa if rec_acc else 0,
        "supplier_dues_paisa": pay_acc.current_balance_paisa if pay_acc else 0,
        "total_revenue_paisa": rev_acc.current_balance_paisa if rev_acc else 0,
        "total_expense_paisa": exp_acc.current_balance_paisa if exp_acc else 0,
        "currency": "BDT",
    }


@merchant_router.post("/sales")
def create_sale(
    req: SaleRequestDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    items_dict = [{"product_id": it.product_id, "quantity": it.quantity} for it in req.items] if req.items else None
    entry = MerchantService.record_sale(
        db=db,
        tenant_id=current_user.tenant_id,
        sale_type=req.sale_type,
        total_amount_paisa=req.total_amount_paisa,
        cash_received_paisa=req.cash_received_paisa,
        party_id=req.party_id,
        items=items_dict,
        request_key=request_key,
    )
    return {"status": "success", "sale_id": entry.id, "entry_number": entry.entry_number}


@merchant_router.post("/collect-due")
def collect_due(
    req: DebtCollectionDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    entry = MerchantService.record_debt_collection(
        db=db,
        tenant_id=current_user.tenant_id,
        party_id=req.party_id,
        amount_paisa=req.amount_paisa,
        request_key=request_key,
    )
    return {"status": "success", "entry_id": entry.id}


@merchant_router.post("/transfer")
def transfer_funds(
    req: TransferDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    entry = MerchantService.record_wallet_transfer(
        db=db,
        tenant_id=current_user.tenant_id,
        from_channel=req.from_channel,
        to_channel=req.to_channel,
        principal_paisa=req.principal_paisa,
        fee_paisa=req.fee_paisa,
        request_key=request_key,
    )
    return {"status": "success", "transfer_id": entry.id}


@merchant_router.post("/cash-close")
def close_cash(
    req: CashCloseDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    snap = MerchantService.record_cash_close(
        db=db,
        tenant_id=current_user.tenant_id,
        snapshot_date=req.snapshot_date,
        actual_drawer_cash_paisa=req.actual_drawer_cash_paisa,
    )
    return {
        "status": "closed",
        "snapshot_date": snap.snapshot_date,
        "closing_cash_paisa": snap.closing_cash_paisa,
        "actual_drawer_cash_paisa": snap.actual_drawer_cash_paisa,
        "discrepancy_paisa": snap.discrepancy_paisa,
    }


@merchant_router.post("/expenses")
def create_expense(
    req: ExpenseCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    entry = MerchantService.record_expense(
        db=db,
        tenant_id=current_user.tenant_id,
        amount_paisa=req.amount_paisa,
        description=req.description,
        category=req.category,
        request_key=request_key,
    )
    return {"status": "success", "expense_id": entry.id}


@merchant_router.post("/withdrawals")
def create_withdrawal(
    req: WithdrawalCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    try:
        entry = MerchantService.record_owner_withdrawal(
            db=db,
            tenant_id=current_user.tenant_id,
            amount_paisa=req.amount_paisa,
            user_role=current_user.role,
        request_key=request_key,
        )
        return {"status": "success", "withdrawal_id": entry.id}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@merchant_router.post("/supplier-payment")
def pay_supplier(
    req: SupplierPaymentDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_key:Optional[str]=Header(None,alias="Idempotency-Key"),
):
    entry = MerchantService.record_supplier_payment(
        db=db,
        tenant_id=current_user.tenant_id,
        party_id=req.party_id,
        amount_paisa=req.amount_paisa,
        channel=req.channel,
        request_key=request_key,
    )
    return {"status": "success", "payment_id": entry.id}


@merchant_router.get("/parties")
def list_parties(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parties = db.query(PartyModel).filter(PartyModel.tenant_id == current_user.tenant_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "phone": p.phone,
            "party_type": p.party_type,
            "current_due_paisa": p.current_due_paisa,
        }
        for p in parties
    ]


@merchant_router.post("/parties")
def create_party(
    req: PartyCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    party = PartyModel(
        tenant_id=current_user.tenant_id,
        name=req.name,
        phone=req.phone,
        party_type=req.party_type,
        current_due_paisa=req.initial_due_paisa,
    )
    db.add(party)
    db.flush()
    if req.initial_due_paisa:
        # Opening party due must also exist in the ledger; it is not new revenue/expense.
        due_code=StandardAccount.RECEIVABLES.value if req.party_type=='customer' else StandardAccount.PAYABLES.value
        due=MerchantService.get_or_create_account(db,current_user.tenant_id,due_code,'Opening party dues','asset' if req.party_type=='customer' else 'liability')
        capital=MerchantService.get_or_create_account(db,current_user.tenant_id,StandardAccount.OWNER_CAPITAL.value,'Owner capital','equity')
        entry=JournalEntryModel(tenant_id=current_user.tenant_id,entry_number='OPEN-'+party.id[:8],event_id='party-opening:'+party.id,description='Verified opening '+req.party_type+' due')
        db.add(entry);db.flush()
        db.add_all([PostingModel(journal_entry_id=entry.id,account_id=due.id,direction='debit' if req.party_type=='customer' else 'credit',amount_paisa=req.initial_due_paisa),PostingModel(journal_entry_id=entry.id,account_id=capital.id,direction='credit' if req.party_type=='customer' else 'debit',amount_paisa=req.initial_due_paisa)])
        db.query(AccountModel).filter_by(id=due.id).update({AccountModel.current_balance_paisa:AccountModel.current_balance_paisa+req.initial_due_paisa},synchronize_session=False)
        capital_delta=req.initial_due_paisa if req.party_type=='customer' else -req.initial_due_paisa
        db.query(AccountModel).filter_by(id=capital.id).update({AccountModel.current_balance_paisa:AccountModel.current_balance_paisa+capital_delta},synchronize_session=False)
    db.commit()
    return {"id": party.id, "name": party.name, "current_due_paisa": party.current_due_paisa}


@merchant_router.get("/products")
def list_products(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    products = db.query(ProductItemModel).filter(ProductItemModel.tenant_id == current_user.tenant_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "unit": p.unit,
            "quantity_on_hand": p.quantity_on_hand,
            "cost_price_paisa": p.cost_price_paisa,
            "selling_price_paisa": p.selling_price_paisa,
        }
        for p in products
    ]


@merchant_router.post("/products")
def create_product(
    req: ProductCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prod = ProductItemModel(
        tenant_id=current_user.tenant_id,
        name=req.name,
        sku=req.sku,
        unit=req.unit,
        quantity_on_hand=req.quantity_on_hand,
        cost_price_paisa=req.cost_price_paisa,
        selling_price_paisa=req.selling_price_paisa,
    )
    db.add(prod)
    db.commit()
    return {"id": prod.id, "name": prod.name, "quantity_on_hand": prod.quantity_on_hand}
