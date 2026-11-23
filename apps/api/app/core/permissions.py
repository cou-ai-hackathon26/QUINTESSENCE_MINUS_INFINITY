"""
Role-Based Authorization & Tenant Isolation Checks.
Restricts actions based on Owner, Cashier, Accountant roles.
Guarantees cross-tenant boundary protection.
"""
from typing import Callable, List
from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.persistence.models import UserModel


def require_role(allowed_roles: List[str]) -> Callable:
    def dependency(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of {allowed_roles}, but current role is '{current_user.role}'.",
            )
        return current_user

    return dependency


def verify_tenant_ownership(resource_tenant_id: str, user_tenant_id: str) -> None:
    """Enforces strict tenant isolation. Throws 403 if tenants mismatch."""
    if resource_tenant_id != user_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Resource belongs to another tenant.",
        )
