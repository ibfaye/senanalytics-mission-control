"""Sen'Analytics Mission Control — FastAPI Backend

Phase 2: LangGraph integration, WebSocket streaming, agent mesh, human-in-the-loop.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.event_bus import event_bus
from app.core.websocket import ws_manager
from app.core.database import db
from app.core.neo4j_client import neo4j
from app.config import settings
from app.api import executions, approvals, agents
from app.api import mcp as mcp_api
from app.api import knowledge as knowledge_api
from app.api import dashboards as dashboards_api
from app.api import reports as reports_api
from app.api import organizations as orgs_api
from app.api import audit as audit_api
from app.api import workflows as workflows_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("[Mission Control] Starting up...")
    await event_bus.connect()
    await db.connect()
    await neo4j.connect()
    logger.info(f"[Mission Control] Ready. DB: {db.is_connected}, Neo4j: {neo4j.is_connected}")
    yield
    logger.info("[Mission Control] Shutting down...")
    await db.disconnect()
    await neo4j.disconnect()


app = FastAPI(
    title="Sen'Analytics Mission Control API",
    description="Agentic Governance Operating System — Backend API",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
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
app.include_router(dashboards_api.router)
app.include_router(reports_api.router)
app.include_router(orgs_api.router)
app.include_router(audit_api.router)
app.include_router(workflows_api.router)


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
        "postgres": "connected" if db.is_connected else "disconnected",
        "neo4j": "connected" if neo4j.is_connected else "disconnected",
    }
