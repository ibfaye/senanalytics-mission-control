"""Audit API — query the immutable audit trail."""

from fastapi import APIRouter, Query
from app.core.database import db

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
async def list_audit_logs(
    execution_id: str | None = Query(None),
    workflow_id: str | None = Query(None),
    action_type: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Query audit logs with optional filters.
    Returns the most recent entries first (immutable append-only log).
    Falls back to in-memory demo data when DB is unavailable.
    """
    if not db.is_connected:
        return _demo_audit_logs(execution_id, workflow_id, action_type, limit)

    conditions = []
    params: list = []
    param_idx = 1

    if execution_id:
        conditions.append(f"execution_id = ${param_idx}::uuid")
        params.append(execution_id)
        param_idx += 1
    if workflow_id:
        conditions.append(f"workflow_id = ${param_idx}::uuid")
        params.append(workflow_id)
        param_idx += 1
    if action_type:
        conditions.append(f"action_type = ${param_idx}::audit_action_type")
        params.append(action_type)
        param_idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""SELECT id, execution_id, workflow_id, action, action_type,
                        actor_email, details, created_at
                 FROM audit_logs {where}
                 ORDER BY created_at DESC
                 LIMIT ${param_idx}"""
    params.append(limit)

    rows = await db.fetch(query, *params)
    return [_format_audit_row(r) for r in rows]


def _format_audit_row(row: dict) -> dict:
    return {
        "id": str(row["id"]),
        "execution_id": str(row["execution_id"]) if row.get("execution_id") else None,
        "workflow_id": str(row["workflow_id"]) if row.get("workflow_id") else None,
        "action": row["action"],
        "action_type": row["action_type"],
        "actor_email": row.get("actor_email", "system"),
        "details": row.get("details") or {},
        "created_at": str(row["created_at"]),
    }


def _demo_audit_logs(
    execution_id: str | None,
    workflow_id: str | None,
    action_type: str | None,
    limit: int,
) -> list[dict]:
    """In-memory demo data when PostgreSQL isn't connected."""
    logs = [
        {"action": "workflow.complete", "action_type": "workflow_executed",
         "actor_email": "system", "details": {"agents_executed": 4, "total_tokens": 2890},
         "created_at": "2026-06-07T14:30:00Z"},
        {"action": "node.complete.reporting", "action_type": "node_completed",
         "actor_email": "system", "details": {"node_label": "Reporting Agent", "execution_time_ms": 380},
         "created_at": "2026-06-07T14:29:55Z"},
        {"action": "node.complete.compliance", "action_type": "node_completed",
         "actor_email": "system", "details": {"node_label": "Compliance Agent", "execution_time_ms": 750},
         "created_at": "2026-06-07T14:29:50Z"},
        {"action": "approval.approved", "action_type": "approval_granted",
         "actor_email": "ibfaye", "details": {"decision": "approved", "node_label": "Human Approval"},
         "created_at": "2026-06-07T14:29:45Z"},
        {"action": "approval.request", "action_type": "approval_requested",
         "actor_email": "system", "details": {"node_label": "Human Approval"},
         "created_at": "2026-06-07T14:29:40Z"},
        {"action": "node.complete.classification", "action_type": "node_completed",
         "actor_email": "system", "details": {"node_label": "Classification Agent", "execution_time_ms": 680},
         "created_at": "2026-06-07T14:29:35Z"},
        {"action": "node.complete.discovery", "action_type": "node_completed",
         "actor_email": "system", "details": {"node_label": "Discovery Agent", "execution_time_ms": 450},
         "created_at": "2026-06-07T14:29:30Z"},
        {"action": "workflow.execute", "action_type": "workflow_executed",
         "actor_email": "system", "details": {"workflow_name": "GDPR Compliance Audit"},
         "created_at": "2026-06-07T14:29:25Z"},
    ]

    # Apply filters
    if action_type:
        logs = [l for l in logs if l["action_type"] == action_type]
    return logs[:limit]
