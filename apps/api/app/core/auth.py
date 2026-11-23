"""
Authentication & JWT Session Management.
Enforces real session validation, role assignment, and demo tenant separation.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status, Request
import hashlib
import secrets
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.persistence.models import TenantModel, UserModel, RevokedSessionModel

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class TokenData(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    is_demo: bool


def create_access_token(user_id: str, tenant_id: str, role: str, is_demo: bool = False) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "jti": secrets.token_hex(16),
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "is_demo": is_demo,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload["role"],
            is_demo=payload.get("is_demo", False),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except (jwt.InvalidTokenError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )


def get_current_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    token = auth.credentials if auth and auth.credentials else request.cookies.get('shongoti_session')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token.",
        )

    if not auth and request.method not in ('GET','HEAD','OPTIONS'):
        allowed=set(settings.cors_origins)|{str(request.base_url).rstrip('/')}
        if request.headers.get('origin') not in allowed:
            raise HTTPException(403,'Same-origin request required for cookie-authenticated writes.')
    if db.get(RevokedSessionModel, hashlib.sha256(token.encode()).hexdigest()):
        raise HTTPException(401,'Session has been revoked. Sign in again.')
    token_data = decode_access_token(token)
    user = (
        db.query(UserModel)
        .filter(UserModel.id == token_data.user_id, UserModel.tenant_id == token_data.tenant_id)
        .first()
    )
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )
    return user


def get_or_create_demo_tenant(db: Session) -> tuple[TenantModel, UserModel]:
    """Ensures a seeded synthetic demo tenant exists with is_demo=True."""
    demo_tenant = db.query(TenantModel).filter(TenantModel.id == "demo-tenant-001").first()
    if not demo_tenant:
        demo_tenant = TenantModel(
            id="demo-tenant-001",
            name="ভাই ভাই জেনারেল স্টোর (ডেমো)",
            currency="BDT",
            is_demo=True,
        )
        db.add(demo_tenant)
        db.flush()

    demo_user = db.query(UserModel).filter(UserModel.id == "demo-user-001").first()
    if not demo_user:
        demo_user = UserModel(
            id="demo-user-001",
            tenant_id=demo_tenant.id,
            phone="01700000000",
            role="owner",
            is_active=True,
        )
        db.add(demo_user)
        db.commit()

    return demo_tenant, demo_user
