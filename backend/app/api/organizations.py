"""Organizations API — manage tenancy, members, and RBAC."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.organizations import org_store, UserRole
from app.core.rbac import get_current_user, require_admin, require_editor_or_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


class CreateOrgRequest(BaseModel):
    name: str
    slug: str
    plan: str = "free"


class AddMemberRequest(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    role: str = "viewer"


class UpdateRoleRequest(BaseModel):
    role: str


@router.get("/")
async def list_organizations(user: dict = Depends(get_current_user)):
    """List all organizations (public info only)."""
    orgs = org_store.list_orgs()
    return [
        {"id": o.id, "name": o.name, "slug": o.slug, "plan": o.plan, "member_count": len(org_store.get_members(o.id))}
        for o in orgs
    ]


@router.get("/current")
async def current_organization(user: dict = Depends(get_current_user)):
    """Get the current user's organization context."""
    org_id = user.get("org_id") or org_store.get_user_org(user["user_id"])
    if not org_id:
        raise HTTPException(status_code=404, detail="No organization found")

    org = org_store.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    member = org_store.get_member(org_id, user["user_id"])

    return {
        "organization": org.model_dump(),
        "user": {
            "user_id": user["user_id"],
            "user_name": user.get("user_name"),
            "user_email": user.get("user_email"),
            "role": member.role.value if member else "unknown",
        },
        "permissions": [p.value for p in UserRole] if member else [],
    }


@router.post("/")
async def create_organization(body: CreateOrgRequest, user: dict = Depends(require_admin)):
    """Create a new organization (admin only)."""
    org = org_store.create_org(body.name, body.slug, body.plan)
    org_store.add_member(org.id, user["user_id"], user.get("user_name", ""),
                         user.get("user_email", ""), UserRole.ADMIN)
    return org.model_dump()


@router.delete("/{org_id}")
async def delete_organization(org_id: str, user: dict = Depends(require_admin)):
    """Delete an organization (admin only)."""
    if not org_store.delete_org(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"message": "Organization deleted"}


# ── Members ──

@router.get("/{org_id}/members")
async def list_members(org_id: str, user: dict = Depends(get_current_user)):
    """List members of an organization."""
    org = org_store.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    members = org_store.get_members(org_id)
    return [
        {
            "user_id": m.user_id, "user_name": m.user_name,
            "user_email": m.user_email, "role": m.role.value,
            "joined_at": m.joined_at,
        }
        for m in members
    ]


@router.post("/{org_id}/members")
async def add_member(org_id: str, body: AddMemberRequest,
                     user: dict = Depends(require_admin)):
    """Add a member to an organization (admin only)."""
    try:
        role = UserRole(body.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {body.role}")

    member = org_store.add_member(
        org_id, body.user_id, body.user_name, body.user_email, role,
    )
    if not member:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "user_id": member.user_id, "user_name": member.user_name,
        "role": member.role.value, "joined_at": member.joined_at,
    }


@router.delete("/{org_id}/members/{user_id}")
async def remove_member(org_id: str, user_id: str,
                        user: dict = Depends(require_admin)):
    """Remove a member from an organization (admin only)."""
    if not org_store.remove_member(org_id, user_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member removed"}


@router.put("/{org_id}/members/{user_id}/role")
async def update_member_role(org_id: str, user_id: str, body: UpdateRoleRequest,
                             user: dict = Depends(require_admin)):
    """Update a member's role (admin only)."""
    try:
        role = UserRole(body.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {body.role}")

    if not org_store.update_role(org_id, user_id, role):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": f"Role updated to {role.value}"}
