"""
API Router endpoints for Authentication, Ledger, and Obligations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user, get_or_create_demo_tenant
from app.core.database import get_db
from app.core.permissions import require_role
from app.persistence.models import (
    AccountModel,
    JournalEntryModel,
    ObligationModel,
    PostingModel,
    TenantModel,
    UserModel,
    generate_uuid,
)

api_router = APIRouter(prefix="/api/v1")


# --- Auth Models & Routes ---

class LoginRequest(BaseModel):
    phone: str
    otp: str
    role: Optional[str] = "owner"
    tenant_id: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str
    is_demo: bool


@api_router.post("/auth/demo-session", response_model=AuthResponse, tags=["Auth"])
def get_demo_session(db: Session = Depends(get_db)):
    """Provides a synthetic demo session strictly isolated in demo tenancy."""
    from app.core.config import settings
    if not settings.ALLOW_LEGACY_TEST_AUTH:raise HTTPException(410,'Shared test sessions are disabled. Use the isolated judge account entry.')
    tenant, user = get_or_create_demo_tenant(db)
    token = create_access_token(user.id, tenant.id, user.role, is_demo=True)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
        is_demo=True,
    )


@api_router.post("/auth/login", response_model=AuthResponse, tags=["Auth"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Validates phone and OTP.
    In local dev mode, OTP '123456' is accepted for registered numbers or creates initial owner.
    """
    from app.core.config import settings
    if not settings.ALLOW_LEGACY_TEST_AUTH or settings.ENVIRONMENT == 'production':
        raise HTTPException(status_code=503, detail='OTP sender is not configured. Use the credential sign-in flow.')
    if req.otp != "123456":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code.")

    from app.persistence.models import UserCredentialModel
    if db.query(UserCredentialModel).filter_by(phone=req.phone).first():
        raise HTTPException(status_code=401, detail='This account requires password sign-in.')

    user = db.query(UserModel).filter(UserModel.phone == req.phone).first()
    if not user:
        if req.tenant_id:
            tenant = db.query(TenantModel).filter(TenantModel.id == req.tenant_id).first()
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
            # Unauthenticated registration against an existing tenant defaults strictly to cashier
            # to prevent self-assigning owner/manager privileges.
            user_role = "cashier"
        else:
            tenant = TenantModel(name=f"Shop {req.phone[-4:]}", currency="BDT", is_demo=False)
            db.add(tenant)
            db.flush()
            user_role = req.role or "owner"

        user = UserModel(tenant_id=tenant.id, phone=req.phone, role=user_role, is_active=True)
        db.add(user)
        db.commit()
    else:
        tenant = user.tenant

    token = create_access_token(user.id, tenant.id, user.role, is_demo=tenant.is_demo)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
        is_demo=tenant.is_demo,
    )


# --- Ledger Models & Routes ---

class PostingDTO(BaseModel):
    account_code: str
    direction: str = Field(..., pattern="^(debit|credit)$")
    amount_paisa: int = Field(..., gt=0)


class JournalPostRequest(BaseModel):
    description: str
    event_id: Optional[str] = None
    postings: List[PostingDTO]


@api_router.get("/ledger/accounts", tags=["Ledger"])
def list_accounts(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists accounts strictly belonging to the authenticated tenant."""
    accounts = (
        db.query(AccountModel)
        .filter(AccountModel.tenant_id == current_user.tenant_id)
        .all()
    )
    return [
        {
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "type": acc.type,
            "current_balance_paisa": acc.current_balance_paisa,
        }
        for acc in accounts
    ]


@api_router.post("/ledger/post", tags=["Ledger"])
def post_journal_entry(
    req: JournalPostRequest,
    current_user: UserModel = Depends(require_role(['owner','accountant'])),
    db: Session = Depends(get_db),
):
    """
    Enforces balanced posting, idempotency (duplicate event_id rejection),
    and tenant isolation.
    """
    # 1. Enforce balanced equation: sum(debits) == sum(credits)
    debits = sum(p.amount_paisa for p in req.postings if p.direction == "debit")
    credits = sum(p.amount_paisa for p in req.postings if p.direction == "credit")
    if debits != credits:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unbalanced journal entry: debits={debits} != credits={credits}.",
        )

    # 2. Check duplicate event_id for idempotency
    if req.event_id:
        existing = (
            db.query(JournalEntryModel)
            .filter(
                JournalEntryModel.tenant_id == current_user.tenant_id,
                JournalEntryModel.event_id == req.event_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate event_id '{req.event_id}' already processed.",
            )

    # 3. Role enforcement: only owner and accountant can post journal entries; cashier cannot do owner draws
    if any(p.account_code == "equity:owner_draw" for p in req.postings):
        if current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Only owners can authorize equity withdrawals.",
            )

    # 4. Resolve or create accounts within tenant
    entry = JournalEntryModel(
        tenant_id=current_user.tenant_id,
        entry_number=f"JN-{generate_uuid()[:8].upper()}",
        description=req.description,
        event_id=req.event_id,
    )
    db.add(entry)
    db.flush()

    for p in req.postings:
        account = (
            db.query(AccountModel)
            .filter(
                AccountModel.tenant_id == current_user.tenant_id,
                AccountModel.code == p.account_code,
            )
            .first()
        )
        if not account:
            account = AccountModel(
                tenant_id=current_user.tenant_id,
                code=p.account_code,
                name=p.account_code.split(":")[-1].title(),
                type=p.account_code.split(":")[0],
                current_balance_paisa=0,
            )
            db.add(account)
            db.flush()

        posting_record = PostingModel(
            journal_entry_id=entry.id,
            account_id=account.id,
            direction=p.direction,
            amount_paisa=p.amount_paisa,
        )
        db.add(posting_record)

        normal_debit=account.type in ['asset','expense'] or account.code=='equity:owner_draw'
        delta=p.amount_paisa if (p.direction=='debit')==normal_debit else -p.amount_paisa
        update=db.query(AccountModel).filter_by(id=account.id,tenant_id=current_user.tenant_id)
        if delta<0 and account.type=='asset':update=update.filter(AccountModel.current_balance_paisa>=-delta)
        if update.update({AccountModel.current_balance_paisa:AccountModel.current_balance_paisa+delta},synchronize_session=False)!=1:
            db.rollback();raise HTTPException(422,'This entry exceeds the verified asset balance; nothing was posted.')

    db.commit()
    return {"status": "posted", "entry_id": entry.id, "entry_number": entry.entry_number}
