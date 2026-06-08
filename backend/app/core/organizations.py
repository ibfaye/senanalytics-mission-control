"""
Multi-Tenant Organizations — org model, membership, and data scoping.
In-memory for demo; PostgreSQL-backed in production.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    AUDITOR = "auditor"


ROLE_PERMISSIONS: dict[UserRole, list[str]] = {
    UserRole.ADMIN: ["org:read", "org:write", "org:delete", "user:manage",
                     "workflow:read", "workflow:write", "workflow:execute",
                     "agent:read", "agent:manage", "mcp:manage",
                     "audit:read", "report:generate", "approval:resolve"],
    UserRole.EDITOR: ["org:read", "workflow:read", "workflow:write", "workflow:execute",
                      "agent:read", "mcp:read", "report:generate", "approval:resolve"],
    UserRole.VIEWER: ["org:read", "workflow:read", "agent:read", "audit:read", "report:read"],
    UserRole.AUDITOR: ["org:read", "audit:read", "report:read", "report:generate",
                       "workflow:read", "agent:read"],
}


class Organization(BaseModel):
    id: str
    name: str
    slug: str
    plan: str = "free"  # free, pro, enterprise
    settings: dict = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Member(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    organization_id: str
    role: UserRole
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OrganizationStore:
    """In-memory organization and membership store."""

    def __init__(self):
        self._orgs: dict[str, Organization] = {}
        self._members: dict[str, list[Member]] = {}  # org_id → members
        self._user_orgs: dict[str, str] = {}  # user_id → active_org_id

    # ── Organizations ──

    def create_org(self, name: str, slug: str, plan: str = "free") -> Organization:
        import uuid
        org_id = str(uuid.uuid4())[:8]
        org = Organization(id=org_id, name=name, slug=slug, plan=plan)
        self._orgs[org_id] = org
        self._members[org_id] = []
        logger.info(f"[Org] Created '{name}' ({org_id})")
        return org

    def get_org(self, org_id: str) -> Optional[Organization]:
        return self._orgs.get(org_id)

    def list_orgs(self) -> list[Organization]:
        return list(self._orgs.values())

    def delete_org(self, org_id: str) -> bool:
        if org_id in self._orgs:
            del self._orgs[org_id]
            self._members.pop(org_id, None)
            return True
        return False

    # ── Members ──

    def add_member(self, org_id: str, user_id: str, user_name: str,
                   user_email: str, role: UserRole = UserRole.VIEWER) -> Optional[Member]:
        if org_id not in self._orgs:
            return None
        member = Member(
            user_id=user_id, user_name=user_name, user_email=user_email,
            organization_id=org_id, role=role,
        )
        self._members.setdefault(org_id, []).append(member)
        self._user_orgs[user_id] = org_id
        logger.info(f"[Org] Added {user_name} to '{self._orgs[org_id].name}' as {role.value}")
        return member

    def remove_member(self, org_id: str, user_id: str) -> bool:
        if org_id in self._members:
            before = len(self._members[org_id])
            self._members[org_id] = [m for m in self._members[org_id] if m.user_id != user_id]
            if user_id in self._user_orgs:
                del self._user_orgs[user_id]
            return len(self._members[org_id]) < before
        return False

    def get_members(self, org_id: str) -> list[Member]:
        return self._members.get(org_id, [])

    def get_user_org(self, user_id: str) -> Optional[str]:
        return self._user_orgs.get(user_id)

    def get_member(self, org_id: str, user_id: str) -> Optional[Member]:
        for m in self._members.get(org_id, []):
            if m.user_id == user_id:
                return m
        return None

    def update_role(self, org_id: str, user_id: str, role: UserRole) -> bool:
        member = self.get_member(org_id, user_id)
        if member:
            member.role = role
            return True
        return False

    # ── Permissions ──

    def has_permission(self, user_id: str, permission: str, org_id: str = None) -> bool:
        if not org_id:
            org_id = self._user_orgs.get(user_id)
        if not org_id:
            return False
        member = self.get_member(org_id, user_id)
        if not member:
            return False
        allowed = ROLE_PERMISSIONS.get(member.role, [])
        return permission in allowed


# Singleton
org_store = OrganizationStore()


# ── Seed demo org ──

def seed_demo_org():
    """Create default organization with demo users."""
    if org_store.list_orgs():
        return

    org = org_store.create_org(
        name="Sen'Analytics",
        slug="senanalytics",
        plan="enterprise",
    )
    org_store.add_member(org.id, "user-ibfaye", "Ibrahim Faye",
                         "iboufaye2000@hotmail.com", UserRole.ADMIN)
    org_store.add_member(org.id, "user-aminata", "Aminata Diop",
                         "aminata@example.com", UserRole.EDITOR)
    org_store.add_member(org.id, "user-auditor", "Audit Team",
                         "audit@example.com", UserRole.AUDITOR)
    logger.info(f"[Org] Seeded demo org '{org.name}' with 3 members")


seed_demo_org()
