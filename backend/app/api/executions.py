"""Execution API — trigger, monitor, and manage workflow executions."""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.engine import execute_workflow, get_execution, get_pending_approvals, pause_execution, resume_execution, cancel_execution

logger = logging.getLogger(__name__)

router = APIRouter(tags=["executions"])


@router.post("/api/workflows/{workflow_id}/execute")
async def execute(workflow_id: str, background_tasks: BackgroundTasks, input: dict | None = None):
    """
    Execute a workflow. Returns immediately with execution ID.
    Execution runs in background with live WebSocket streaming.
    """
    import uuid as _uuid

    # For now, use demo workflow data from the Phase 1 endpoints
    # In full production, fetch from DB
    workflow = _get_demo_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])

    # Pre-generate execution_id so we can return it immediately
    execution_id = str(_uuid.uuid4())

    # Start execution in background
    background_tasks.add_task(
        execute_workflow,
        workflow_id=workflow_id,
        workflow_nodes=nodes,
        workflow_edges=edges,
        task=workflow.get("name", "Execute governance workflow"),
        input_data=input,
        execution_id=execution_id,
    )

    # Return immediately — frontend connects via WebSocket for updates
    return {
        "message": "Execution started",
        "execution_id": execution_id,
        "workflow_id": workflow_id,
        "status": "running",
    }


@router.get("/api/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get current status of an execution."""
    exec_data = get_execution(execution_id)
    if not exec_data:
        raise HTTPException(status_code=404, detail="Execution not found")
    return exec_data


@router.get("/api/executions")
async def list_executions():
    """List recent executions."""
    from app.core.engine import _executions
    return list(_executions.values())[-20:]  # Last 20


@router.post("/api/executions/{execution_id}/pause")
async def pause_execution_endpoint(execution_id: str):
    """Pause a running execution."""
    if not pause_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or not running")
    return {"message": "Execution paused", "execution_id": execution_id}


@router.post("/api/executions/{execution_id}/resume")
async def resume_execution_endpoint(execution_id: str):
    """Resume a paused execution."""
    if not resume_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or not paused")
    return {"message": "Execution resumed", "execution_id": execution_id}


@router.post("/api/executions/{execution_id}/cancel")
async def cancel_execution_endpoint(execution_id: str):
    """Cancel a running or paused execution."""
    if not cancel_execution(execution_id):
        raise HTTPException(status_code=404, detail="Execution not found or not running/paused")
    return {"message": "Execution cancelled", "execution_id": execution_id}


def _get_demo_workflow(workflow_id: str) -> dict | None:
    """Return the demo GDPR Compliance Audit workflow."""
    return {
        "id": workflow_id,
        "name": "GDPR Compliance Audit",
        "description": "Full GDPR compliance scan across all data assets",
        "status": "active",
        "version": 2,
        "createdBy": "ibfaye",
        "tags": ["gdpr", "compliance"],
        "nodes": [
            {"id": "n1", "nodeType": "trigger", "label": "Manual Trigger", "positionX": 100, "positionY": 200, "config": {}, "status": "idle"},
            {"id": "n2", "nodeType": "agent", "label": "Discovery Agent", "positionX": 350, "positionY": 150, "config": {"agentType": "discovery", "description": "Discover and catalog data sources"}, "status": "idle"},
            {"id": "n3", "nodeType": "agent", "label": "Classification Agent", "positionX": 350, "positionY": 300, "config": {"agentType": "classification", "description": "Classify PII and sensitive data"}, "status": "idle"},
            {"id": "n4", "nodeType": "approval", "label": "Human Approval", "positionX": 600, "positionY": 200, "config": {"description": "Review and approve classification results"}, "status": "idle"},
            {"id": "n5", "nodeType": "agent", "label": "Compliance Agent", "positionX": 850, "positionY": 120, "config": {"agentType": "compliance", "description": "GDPR compliance mapping"}, "status": "idle"},
            {"id": "n6", "nodeType": "agent", "label": "Reporting Agent", "positionX": 850, "positionY": 280, "config": {"agentType": "reporting", "description": "Generate compliance report"}, "status": "idle"},
        ],
        "edges": [
            {"id": "e1", "sourceNodeId": "n1", "targetNodeId": "n2", "edgeType": "smoothstep", "animated": True},
            {"id": "e2", "sourceNodeId": "n1", "targetNodeId": "n3", "edgeType": "smoothstep", "animated": True},
            {"id": "e3", "sourceNodeId": "n2", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
            {"id": "e4", "sourceNodeId": "n3", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
            {"id": "e5", "sourceNodeId": "n4", "targetNodeId": "n5", "edgeType": "smoothstep", "animated": True},
            {"id": "e6", "sourceNodeId": "n4", "targetNodeId": "n6", "edgeType": "smoothstep", "animated": True},
        ],
    }
