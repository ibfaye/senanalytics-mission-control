"""Execution API — trigger, monitor, and manage workflow executions."""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.engine import execute_workflow, get_execution, get_pending_approvals, pause_execution, resume_execution, cancel_execution

logger = logging.getLogger(__name__)

router = APIRouter(tags=["executions"])


async def _fetch_workflow(workflow_id: str) -> dict | None:
    """Fetch workflow with nodes/edges from the workflows API."""
    # Import here to avoid circular imports
    from app.api.workflows import _get_demo as get_wf_demo
    
    # Try DB-backed API first (imports workflows router's logic)
    try:
        # Use the workflows module's get_workflow logic
        from app.core.database import db
        if db.is_connected:
            row = await db.fetchrow(
                "SELECT id, name, description FROM workflows "
                "WHERE id = $1::varchar AND deleted_at IS NULL",
                workflow_id,
            )
            if row:
                # Fetch nodes
                node_rows = await db.fetch(
                    "SELECT id, node_type, label, position_x, position_y, config, status "
                    "FROM workflow_nodes WHERE workflow_id = $1::varchar",
                    workflow_id,
                )
                # Fetch edges
                edge_rows = await db.fetch(
                    "SELECT id, source_node_id, target_node_id, edge_type, label, animated "
                    "FROM workflow_edges WHERE workflow_id = $1::varchar",
                    workflow_id,
                )
                
                if node_rows or edge_rows:
                    return {
                        "id": workflow_id,
                        "name": row.get("name", "Workflow"),
                        "description": row.get("description", ""),
                        "nodes": [
                            {
                                "id": str(r["id"]),
                                "nodeType": r["node_type"],
                                "label": r["label"],
                                "positionX": r["position_x"],
                                "positionY": r["position_y"],
                                "config": r.get("config") or {},
                                "status": r.get("status", "idle"),
                            }
                            for r in node_rows
                        ],
                        "edges": [
                            {
                                "id": str(r["id"]),
                                "sourceNodeId": str(r["source_node_id"]),
                                "targetNodeId": str(r["target_node_id"]),
                                "edgeType": r.get("edge_type", "smoothstep"),
                                "animated": r.get("animated", True),
                            }
                            for r in edge_rows
                        ],
                    }
    except Exception as e:
        logger.warning(f"[Execution] DB fetch for workflow {workflow_id} failed: {e}")
    
    # Fallback: use in-memory demo data
    for wf in get_wf_demo():
        if wf["id"] == workflow_id:
            return wf
    
    return None


@router.post("/api/workflows/{workflow_id}/execute")
async def execute(workflow_id: str, background_tasks: BackgroundTasks, input: dict | None = None):
    """
    Execute a workflow with its actual nodes and edges.
    """
    import uuid as _uuid

    workflow = await _fetch_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])

    # Fall back to demo graph if workflow has no nodes yet
    if not nodes:
        logger.info(f"[Execution] Workflow {workflow_id} has no nodes — using demo graph")
        # Load default demo graph (wf-001) as a starting point
        from app.api.workflows import _get_demo as get_wf_demo
        for wf in get_wf_demo():
            if wf["id"] == "wf-001":
                nodes = wf["nodes"]
                edges = wf["edges"]
                break

    execution_id = str(_uuid.uuid4())

    background_tasks.add_task(
        execute_workflow,
        workflow_id=workflow_id,
        workflow_nodes=nodes,
        workflow_edges=edges,
        task=workflow.get("name", "Execute governance workflow"),
        input_data=input,
        execution_id=execution_id,
    )

    return {
        "message": "Execution started",
        "execution_id": execution_id,
        "workflow_id": workflow_id,
        "status": "running",
    }


@router.get("/api/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    exec_data = get_execution(execution_id)
    if not exec_data:
        raise HTTPException(status_code=404, detail="Execution not found")
    return exec_data


@router.get("/api/executions")
async def list_executions():
    from app.core.database import db
    from app.core.engine import _executions
    
    results = list(_executions.values())[-20:] if _executions else []
    
    # Also fetch from DB
    if db.is_connected:
        try:
            db_rows = await db.fetch(
                "SELECT e.id, e.workflow_id, e.status, e.started_at, e.completed_at, "
                "e.error_message, e.execution_metadata "
                "FROM workflow_executions e "
                "ORDER BY e.started_at DESC NULLS LAST "
                "LIMIT 20"
            )
            for row in db_rows:
                # Skip if already in results
                if any(r.get("id") == str(row["id"]) for r in results):
                    continue
                results.append({
                    "id": str(row["id"]),
                    "workflow_id": str(row["workflow_id"]) if row.get("workflow_id") else "",
                    "status": row["status"],
                    "started_at": row.get("started_at"),
                    "completed_at": row.get("completed_at"),
                    "duration_ms": None,
                    "total_tokens": 0,
                    "total_cost_cents": 0,
                    "error_message": row.get("error_message"),
                    "output": None,
                    "steps": [],
                })
        except Exception as e:
            logger.warning(f"[Executions] DB fetch failed: {e}")
    
    return results


@router.post("/api/executions/{execution_id}/pause")
async def pause_execution_endpoint(execution_id: str):
    if not pause_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or not running")
    return {"message": "Execution paused", "execution_id": execution_id}


@router.post("/api/executions/{execution_id}/resume")
async def resume_execution_endpoint(execution_id: str):
    if not resume_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or not paused")
    return {"message": "Execution resumed", "execution_id": execution_id}


@router.post("/api/executions/{execution_id}/cancel")
async def cancel_execution_endpoint(execution_id: str):
    if not cancel_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
    return {"message": "Execution cancelled", "execution_id": execution_id}
