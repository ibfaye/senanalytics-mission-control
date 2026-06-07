"""Approvals API — resolve human-in-the-loop approval checkpoints."""

import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.core.engine import resolve_approval, get_pending_approvals
from app.core.websocket import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["approvals"])


class ApprovalDecision(BaseModel):
    decision: str  # "approved" | "rejected" | "changes_requested"
    reason: str | None = None


@router.get("/api/approvals")
async def list_pending_approvals():
    """Get all pending approvals across executions."""
    return get_pending_approvals()


@router.post("/api/approvals/{approval_id}/approve")
async def approve(approval_id: str, body: ApprovalDecision | None = None):
    """Approve a pending approval checkpoint."""
    reason = body.reason if body else None
    result = await resolve_approval(approval_id, "approved", reason)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found or already resolved")
    return {"message": "Approval resolved", "approval_id": approval_id, "decision": "approved"}


@router.post("/api/approvals/{approval_id}/reject")
async def reject(approval_id: str, body: ApprovalDecision):
    """Reject a pending approval checkpoint."""
    reason = body.reason or "Rejected by user"
    result = await resolve_approval(approval_id, "rejected", reason)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found or already resolved")
    return {"message": "Approval rejected", "approval_id": approval_id, "decision": "rejected"}
