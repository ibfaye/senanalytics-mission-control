"""
WebSocket Manager — manages active WebSocket connections per workflow execution.
Broadcasts node status updates, approval requests, and execution progress.
"""

import asyncio
import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections grouped by workflow/execution ID."""

    def __init__(self):
        # execution_id -> set of WebSocket connections
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, execution_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if execution_id not in self._connections:
            self._connections[execution_id] = set()
        self._connections[execution_id].add(websocket)
        logger.info(f"[WS] Client connected to execution {execution_id} ({len(self._connections[execution_id])} total)")

    def disconnect(self, execution_id: str, websocket: WebSocket):
        """Remove a disconnected client."""
        if execution_id in self._connections:
            self._connections[execution_id].discard(websocket)
            if not self._connections[execution_id]:
                del self._connections[execution_id]
            logger.info(f"[WS] Client disconnected from execution {execution_id}")

    async def broadcast(self, execution_id: str, event: str, data: dict):
        """Broadcast an event to all clients watching an execution."""
        if execution_id not in self._connections:
            return

        message = json.dumps({"event": event, "data": data}, default=str)
        dead: list[WebSocket] = []

        for ws in self._connections[execution_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(execution_id, ws)

    async def broadcast_node_started(
        self, execution_id: str, node_id: str, node_type: str, node_label: str
    ):
        await self.broadcast(execution_id, "node.started", {
            "execution_id": execution_id,
            "node_id": node_id,
            "node_type": node_type,
            "node_label": node_label,
        })

    async def broadcast_node_completed(
        self, execution_id: str, node_id: str, output: Optional[dict] = None,
        metrics: Optional[dict] = None
    ):
        await self.broadcast(execution_id, "node.completed", {
            "execution_id": execution_id,
            "node_id": node_id,
            "output": output or {},
            "metrics": metrics or {},
        })

    async def broadcast_node_failed(
        self, execution_id: str, node_id: str, error: str, retryable: bool = False
    ):
        await self.broadcast(execution_id, "node.failed", {
            "execution_id": execution_id,
            "node_id": node_id,
            "error": error,
            "retryable": retryable,
        })

    async def broadcast_approval_requested(
        self, execution_id: str, approval_id: str, node_id: str,
        node_label: str, reason: str, context: dict = {}
    ):
        await self.broadcast(execution_id, "approval.requested", {
            "execution_id": execution_id,
            "approval_id": approval_id,
            "node_id": node_id,
            "node_label": node_label,
            "reason": reason,
            "context": context,
        })

    async def broadcast_workflow_completed(
        self, execution_id: str, output: dict
    ):
        await self.broadcast(execution_id, "workflow.execution.completed", {
            "execution_id": execution_id,
            "output": output,
        })

    async def broadcast_workflow_failed(
        self, execution_id: str, error: str
    ):
        await self.broadcast(execution_id, "workflow.execution.failed", {
            "execution_id": execution_id,
            "error": error,
        })

    @property
    def active_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())


# Singleton
ws_manager = ConnectionManager()
