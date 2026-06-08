"""
RBAC Middleware — FastAPI dependency for role-based access control.
Checks user permissions before allowing endpoint access.
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from app.core.organizations import org_store, UserRole


# Simulated auth: extract user from X-User-Id header (NextAuth integration in production)
async def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_user_name: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
) -> dict:
    """Extract current user from headers. Falls back to demo user."""
    user_id = x_user_id or "user-ibfaye"
    org_id = x_org_id or org_store.get_user_org(user_id)

    if not org_id:
        org_id = org_store.list_orgs()[0].id if org_store.list_orgs() else None

    return {
        "user_id": user_id,
        "user_name": x_user_name or "Ibrahim Faye",
        "user_email": x_user_email or "iboufaye2000@hotmail.com",
        "org_id": org_id,
    }


def require_permission(permission: str):
    """Factory: creates a dependency that checks for a specific permission."""

    async def checker(user: dict = Depends(get_current_user)) -> dict:
        has_perm = org_store.has_permission(user["user_id"], permission, user.get("org_id"))
        if not has_perm:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required",
            )
        return user

    return checker


def require_role(*roles: UserRole):
    """Factory: creates a dependency that checks for one of the given roles."""

    async def checker(user: dict = Depends(get_current_user)) -> dict:
        org_id = user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=403, detail="No organization context")

        member = org_store.get_member(org_id, user["user_id"])
        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this organization")

        if member.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{member.role.value}' not allowed. Requires: {[r.value for r in roles]}",
            )
        return user

    return checker


# Convenience aliases
require_admin = require_role(UserRole.ADMIN)
require_editor_or_admin = require_role(UserRole.EDITOR, UserRole.ADMIN)
