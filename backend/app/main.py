"""Sen'Analytics Mission Control — FastAPI Backend

Phase 2: LangGraph integration, WebSocket streaming, agent mesh, human-in-the-loop.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.event_bus import event_bus
from app.core.websocket import ws_manager
from app.api import executions, approvals, agents
from app.api import mcp as mcp_api
from app.api import knowledge as knowledge_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("[Mission Control] Starting up...")
    await event_bus.connect()
    logger.info(f"[Mission Control] Ready. WebSocket manager active.")
    yield
    logger.info("[Mission Control] Shutting down...")


app = FastAPI(
    title="Sen'Analytics Mission Control API",
    description="Agentic Governance Operating System — Backend API",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST Routers ──
app.include_router(executions.router)
app.include_router(approvals.router)
app.include_router(agents.router)
app.include_router(mcp_api.router)
app.include_router(knowledge_api.router)


# ── WebSocket Endpoint ──

@app.websocket("/ws/workflows/{workflow_id}")
async def websocket_workflow(websocket: WebSocket, workflow_id: str):
    """
    WebSocket for live execution streaming.
    Frontend connects here when viewing a workflow canvas.
    Receives: node.{started,completed,failed}, approval.requested, workflow.{completed,failed}
    Sends: approval.respond
    """
    # For simplicity, use workflow_id as the execution channel
    # In production, the frontend passes the execution_id
    execution_id = workflow_id

    await ws_manager.connect(execution_id, websocket)
    logger.info(f"[WS] Client connected to workflow {workflow_id}")

    try:
        while True:
            # Receive messages from client (approval responses)
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "approval.respond":
                payload = data.get("data", {})
                approval_id = payload.get("approvalId")
                decision = payload.get("decision")
                reason = payload.get("reason")

                if approval_id and decision:
                    from app.core.engine import resolve_approval
                    await resolve_approval(approval_id, decision, reason)
                    logger.info(f"[WS] Approval {approval_id} resolved via WebSocket: {decision}")

    except WebSocketDisconnect:
        ws_manager.disconnect(execution_id, websocket)
        logger.info(f"[WS] Client disconnected from workflow {workflow_id}")
    except Exception as e:
        ws_manager.disconnect(execution_id, websocket)
        logger.error(f"[WS] Error in workflow {workflow_id}: {e}")


# ── Health ──

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "version": "0.2.0",
        "service": "senanalytics-mission-control",
        "active_ws_connections": ws_manager.active_connections,
    }


# ── Phase 1: Demo Workflow Data ──

@app.get("/api/workflows")
async def list_workflows():
    return [
        {
            "id": "wf-001", "name": "GDPR Compliance Audit",
            "description": "Full GDPR compliance scan across all data assets",
            "status": "active", "version": 2, "createdBy": "ibfaye",
            "tags": ["gdpr", "compliance"],
            "createdAt": "2026-06-07T10:00:00Z", "updatedAt": "2026-06-07T10:30:00Z",
            "nodes": [], "edges": [],
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


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    return {
        "id": workflow_id, "name": "GDPR Compliance Audit",
        "description": "Full GDPR compliance scan across all data assets",
        "status": "active", "version": 2, "createdBy": "ibfaye",
        "tags": ["gdpr", "compliance"],
        "createdAt": "2026-06-07T10:00:00Z", "updatedAt": "2026-06-07T10:30:00Z",
        "nodes": [
            {"id": "n1", "workflowId": workflow_id, "nodeType": "trigger", "label": "Manual Trigger", "positionX": 100, "positionY": 200, "config": {}, "status": "idle"},
            {"id": "n2", "workflowId": workflow_id, "nodeType": "agent", "label": "Discovery Agent", "positionX": 350, "positionY": 150, "config": {"agentType": "discovery", "description": "Discover and catalog data sources"}, "status": "idle"},
            {"id": "n3", "workflowId": workflow_id, "nodeType": "agent", "label": "Classification Agent", "positionX": 350, "positionY": 300, "config": {"agentType": "classification", "description": "Classify PII and sensitive data"}, "status": "idle"},
            {"id": "n4", "workflowId": workflow_id, "nodeType": "approval", "label": "Human Approval", "positionX": 600, "positionY": 200, "config": {"description": "Review and approve classification results"}, "status": "idle"},
            {"id": "n5", "workflowId": workflow_id, "nodeType": "agent", "label": "Compliance Agent", "positionX": 850, "positionY": 120, "config": {"agentType": "compliance", "description": "GDPR compliance mapping"}, "status": "idle"},
            {"id": "n6", "workflowId": workflow_id, "nodeType": "agent", "label": "Reporting Agent", "positionX": 850, "positionY": 280, "config": {"agentType": "reporting", "description": "Generate compliance report"}, "status": "idle"},
        ],
        "edges": [
            {"id": "e1", "workflowId": workflow_id, "sourceNodeId": "n1", "targetNodeId": "n2", "edgeType": "smoothstep", "animated": True},
            {"id": "e2", "workflowId": workflow_id, "sourceNodeId": "n1", "targetNodeId": "n3", "edgeType": "smoothstep", "animated": True},
            {"id": "e3", "workflowId": workflow_id, "sourceNodeId": "n2", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
            {"id": "e4", "workflowId": workflow_id, "sourceNodeId": "n3", "targetNodeId": "n4", "edgeType": "smoothstep", "animated": True},
            {"id": "e5", "workflowId": workflow_id, "sourceNodeId": "n4", "targetNodeId": "n5", "edgeType": "smoothstep", "animated": True},
            {"id": "e6", "workflowId": workflow_id, "sourceNodeId": "n4", "targetNodeId": "n6", "edgeType": "smoothstep", "animated": True},
        ],
    }
