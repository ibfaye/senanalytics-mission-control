"""Workflows API — CRUD for workflows, nodes, and edges. DB-backed with in-memory fallback."""

import json
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


# ── Pydantic Models ────────────────────────────────────────────

class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] | None = None


class GraphSavePayload(BaseModel):
    nodes: list[dict]
    edges: list[dict]


# ── In-memory fallback (demo data, seeded on first request) ────

_demo_workflows: list[dict] | None = None


def _seed_demo() -> list[dict]:
    """Return demo workflows with full nodes/edges for the in-memory fallback."""
    return [
        {
            "id": "wf-001", "name": "GDPR Compliance Audit",
            "description": "Full GDPR compliance scan across all data assets",
            "status": "active", "version": 2, "createdBy": "ibfaye",
            "tags": ["gdpr", "compliance"],
            "createdAt": "2026-06-07T10:00:00Z", "updatedAt": "2026-06-07T10:30:00Z",
            "nodes": [
                {"id": "n1", "workflowId": "wf-001", "nodeType": "trigger", "label": "Manual Trigger", "positionX": 100, "positionY": 200, "config": {}, "status": "idle"},
                {"id": "n2", "workflowId": "wf-001", "nodeType": "agent", "label": "Discovery Agent", "positionX": 350, "positionY": 150, "config": {"agentType": "discovery", "description": "Discover and catalog data sources"}, "status": "idle"},
                {"id": "n3", "workflowId": "wf-001", "nodeType": "agent", "label": "Classification Agent", "positionX": 350, "positionY": 300, "config": {"agentType": "classification", "description": "Classify PII and sensitive data"}, "status": "idle"},
                {"id": "n4", "workflowId": "wf-001", "nodeType": "approval", "label": "Human Approval", "positionX": 600, "positionY": 200, "config": {"description": "Review and approve classification results"}, "status": "idle"},
                {"id": "n5", "workflowId": "wf-001", "nodeType": "agent", "label": "Compliance Agent", "positionX": 850, "positionY": 120, "config": {"agentType": "compliance", "description": "GDPR compliance mapping"}, "status": "idle"},
                {"id": "n6", "workflowId": "wf-001", "nodeType": "agent", "label": "Reporting Agent", "positionX": 850, "positionY": 280, "config": {"agentType": "reporting", "description": "Generate compliance report"}, "status": "idle"},
            ],
            "edges": [
                {"id": "e1", "workflowId": "wf-001", "sourceNodeId": "n1", "targetNodeId": "n2", "edgeType": "smoothstep", "animated": True},
                {"id": "e2", "workflowId": "wf-001", "sourceNodeId": "n1", "targetNodeId": "n3", "edgeType": "smoothstep", "animated": True},
                {"id": "e3", "workflowId": "wf-001", "sourceNodeId": "n2", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
                {"id": "e4", "workflowId": "wf-001", "sourceNodeId": "n3", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
                {"id": "e5", "workflowId": "wf-001", "sourceNodeId": "n4", "targetNodeId": "n5", "edgeType": "smoothstep", "animated": True},
                {"id": "e6", "workflowId": "wf-001", "sourceNodeId": "n4", "targetNodeId": "n6", "edgeType": "smoothstep", "animated": True},
            ],
        },
        {
            "id": "wf-002", "name": "PII Discovery Scan",
            "description": "Discover and classify PII across customer database",
            "status": "draft", "version": 1, "createdBy": "ibfaye",
            "tags": ["pii", "discovery"],
            "createdAt": "2026-06-07T11:00:00Z", "updatedAt": "2026-06-07T11:00:00Z",
            "nodes": [], "edges": [],
        },
        {
            "id": "wf-003", "name": "Security Posture Review",
            "description": "IAM and encryption review for production systems",
            "status": "active", "version": 3, "createdBy": "ibfaye",
            "tags": ["security", "iam"],
            "createdAt": "2026-06-06T08:00:00Z", "updatedAt": "2026-06-06T15:00:00Z",
            "nodes": [], "edges": [],
        },
    ]


def _get_demo() -> list[dict]:
    global _demo_workflows
    if _demo_workflows is None:
        _demo_workflows = _seed_demo()
    return _demo_workflows


# ── GET /api/workflows ────────────────────────────────────────

@router.get("")
async def list_workflows():
    """List all workflows. DB-backed with in-memory fallback."""
    if db.is_connected:
        rows = await db.fetch(
            """SELECT id, name, description, status, version, tags, metadata,
                      created_at, updated_at
               FROM workflows WHERE deleted_at IS NULL
               ORDER BY updated_at DESC LIMIT 50"""
        )
        return [_format_workflow_row(r) for r in rows]

    return [{k: v for k, v in wf.items() if k not in ("nodes", "edges")}
            for wf in _get_demo()]


# ── GET /api/workflows/{workflow_id} ──────────────────────────

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a workflow with its full graph (nodes + edges)."""
    if db.is_connected:
        wf_row = await db.fetchrow(
            """SELECT id, name, description, status, version, tags, metadata,
                      created_at, updated_at
               FROM workflows WHERE id = $1::uuid AND deleted_at IS NULL""",
            workflow_id,
        )
        if not wf_row:
            raise HTTPException(status_code=404, detail="Workflow not found")

        wf = _format_workflow_row(wf_row)

        # Fetch nodes
        node_rows = await db.fetch(
            """SELECT id, node_type, label, position_x, position_y,
                      width, height, config, status
               FROM workflow_nodes WHERE workflow_id = $1::uuid
               ORDER BY created_at""",
            workflow_id,
        )
        wf["nodes"] = [_format_node_row(r, workflow_id) for r in node_rows]

        # Fetch edges
        edge_rows = await db.fetch(
            """SELECT id, source_node_id, target_node_id, source_handle,
                      target_handle, edge_type, label, animated
               FROM workflow_edges WHERE workflow_id = $1::uuid""",
            workflow_id,
        )
        wf["edges"] = [_format_edge_row(r, workflow_id) for r in edge_rows]

        return wf

    # In-memory fallback
    for wf in _get_demo():
        if wf["id"] == workflow_id:
            return wf
    raise HTTPException(status_code=404, detail="Workflow not found")


# ── POST /api/workflows ───────────────────────────────────────

@router.post("", status_code=201)
async def create_workflow(body: WorkflowCreate):
    """Create a new workflow."""
    if db.is_connected:
        new_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        await db.execute(
            """INSERT INTO workflows (id, name, description, tags, created_at, updated_at)
               VALUES ($1::uuid, $2, $3, $4, $5, $5)""",
            new_id, body.name, body.description, body.tags or [], now,
        )
        return {"id": new_id, "name": body.name, "description": body.description,
                "status": "draft", "version": 1, "tags": body.tags or []}

    # In-memory fallback
    new_id = f"wf-{uuid.uuid4().hex[:4]}"
    new_wf = {
        "id": new_id, "name": body.name, "description": body.description or "",
        "status": "draft", "version": 1, "createdBy": "ibfaye",
        "tags": body.tags or [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "nodes": [], "edges": [],
    }
    _get_demo().append(new_wf)
    return {k: v for k, v in new_wf.items() if k not in ("nodes", "edges")}


# ── PUT /api/workflows/{workflow_id}/nodes ────────────────────

@router.put("/{workflow_id}/nodes")
async def save_graph(workflow_id: str, body: GraphSavePayload):
    """Save the full graph (nodes + edges) for a workflow. Replaces existing graph."""
    if db.is_connected:
        # Verify workflow exists
        exists = await db.fetchval(
            "SELECT id FROM workflows WHERE id = $1::uuid AND deleted_at IS NULL",
            workflow_id,
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Transactional: delete old graph, insert new graph
        async with db.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM workflow_edges WHERE workflow_id = $1::uuid",
                    workflow_id,
                )
                await conn.execute(
                    "DELETE FROM workflow_nodes WHERE workflow_id = $1::uuid",
                    workflow_id,
                )

                # Insert nodes
                node_id_map: dict[str, str] = {}
                for n in body.nodes:
                    new_node_id = str(uuid.uuid4())
                    node_id_map[n["id"]] = new_node_id
                    await conn.execute(
                        """INSERT INTO workflow_nodes
                           (id, workflow_id, node_type, label, position_x, position_y, config, status)
                           VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7::jsonb, $8)""",
                        new_node_id, workflow_id,
                        n.get("nodeType", "agent"),
                        n.get("label", ""),
                        n.get("positionX", 0),
                        n.get("positionY", 0),
                        json.dumps(n.get("config", {})),
                        n.get("status", "idle"),
                    )

                # Insert edges (map old node IDs to new DB IDs)
                for e in body.edges:
                    await conn.execute(
                        """INSERT INTO workflow_edges
                           (id, workflow_id, source_node_id, target_node_id,
                            edge_type, label, animated)
                           VALUES ($1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7)""",
                        str(uuid.uuid4()), workflow_id,
                        node_id_map.get(e.get("sourceNodeId", ""), e.get("sourceNodeId", "")),
                        node_id_map.get(e.get("targetNodeId", ""), e.get("targetNodeId", "")),
                        e.get("edgeType", "smoothstep"),
                        e.get("label"),
                        e.get("animated", False),
                    )

        return {"message": "Graph saved", "workflow_id": workflow_id,
                "nodes": len(body.nodes), "edges": len(body.edges)}

    # In-memory fallback
    for wf in _get_demo():
        if wf["id"] == workflow_id:
            for n in body.nodes:
                n["workflowId"] = workflow_id
            for e in body.edges:
                e["workflowId"] = workflow_id
            wf["nodes"] = body.nodes
            wf["edges"] = body.edges
            wf["updatedAt"] = datetime.now(timezone.utc).isoformat()
            return {"message": "Graph saved (in-memory)", "workflow_id": workflow_id,
                    "nodes": len(body.nodes), "edges": len(body.edges)}

    raise HTTPException(status_code=404, detail="Workflow not found")


# ── Formatting Helpers ─────────────────────────────────────────

def _format_workflow_row(row: dict) -> dict:
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "description": row.get("description") or "",
        "status": row.get("status", "draft"),
        "version": row.get("version", 1),
        "createdBy": "system",  # TODO: real user when auth wired
        "tags": row.get("tags") or [],
        "createdAt": _iso(row.get("created_at")),
        "updatedAt": _iso(row.get("updated_at")),
    }


def _format_node_row(row: dict, workflow_id: str) -> dict:
    return {
        "id": str(row["id"]),
        "workflowId": workflow_id,
        "nodeType": row["node_type"],
        "label": row["label"],
        "positionX": row["position_x"],
        "positionY": row["position_y"],
        "width": row.get("width"),
        "height": row.get("height"),
        "config": row.get("config") or {},
        "status": row.get("status", "idle"),
    }


def _format_edge_row(row: dict, workflow_id: str) -> dict:
    return {
        "id": str(row["id"]),
        "workflowId": workflow_id,
        "sourceNodeId": str(row["source_node_id"]),
        "targetNodeId": str(row["target_node_id"]),
        "sourceHandle": row.get("source_handle"),
        "targetHandle": row.get("target_handle"),
        "edgeType": row.get("edge_type", "smoothstep"),
        "label": row.get("label"),
        "animated": row.get("animated", False),
    }


def _iso(val) -> str:
    if val is None:
        return ""
    return val.isoformat() if hasattr(val, "isoformat") else str(val)
