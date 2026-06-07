"""
Execution Engine — runs workflows through LangGraph with live WebSocket streaming.
"""

import asyncio
import logging
import uuid
from typing import Optional, Any
from datetime import datetime, timezone

from app.graphs.governance_graph import governance_graph, AgentState
from app.core.websocket import ws_manager

logger = logging.getLogger(__name__)

_executions: dict[str, dict] = {}
_pending_approvals: dict[str, asyncio.Event] = {}


async def execute_workflow(
    workflow_id: str,
    workflow_nodes: list[dict],
    workflow_edges: list[dict],
    task: str = "Execute governance workflow",
    input_data: Optional[dict] = None,
) -> dict:
    """
    Execute workflow: run LangGraph, broadcast live events, handle approvals.
    """
    execution_id = str(uuid.uuid4())
    _executions[execution_id] = {
        "id": execution_id, "workflow_id": workflow_id, "status": "running",
        "started_at": datetime.now(timezone.utc), "completed_at": None,
        "steps": [], "output": None, "error": None,
    }

    logger.info(f"[Engine] Starting execution {execution_id}")

    await ws_manager.broadcast(execution_id, "workflow.execution.started", {
        "execution_id": execution_id, "workflow_id": workflow_id, "workflow_name": task,
    })

    # Build plan for human-visible steps (includes approvals)
    full_plan = _build_full_plan(workflow_nodes, workflow_edges)
    agent_plan = [s for s in full_plan if not s.get("requires_approval")]
    logger.info(f"[Engine] Plan: {len(full_plan)} steps ({len(agent_plan)} agent steps)")

    initial_state: AgentState = {
        "messages": [], "task": task, "workflow_id": workflow_id,
        "execution_id": execution_id, "workflow_nodes": workflow_nodes,
        "workflow_edges": workflow_edges, "plan": agent_plan, "current_step": 0,
        "agent_results": {}, "next_agent": "", "current_task_context": {},
        "final_output": None, "errors": [],
    }

    config = {"configurable": {"thread_id": execution_id}}

    try:
        # ── Walk through full plan (agent + approval steps) ──
        agent_step_idx = 0

        for step_idx, step in enumerate(full_plan):
            node_id = step["node_id"]
            node_label = step["node_label"]

            # ── Approval step ──
            if step.get("requires_approval"):
                approval_id = str(uuid.uuid4())
                await ws_manager.broadcast_approval_requested(
                    execution_id, approval_id, node_id, node_label,
                    step.get("description", "Human approval required"), {}
                )
                _executions[execution_id].setdefault("approvals", []).append({
                    "approval_id": approval_id, "node_id": node_id, "status": "pending",
                })

                event = asyncio.Event()
                _pending_approvals[approval_id] = event
                try:
                    await asyncio.wait_for(event.wait(), timeout=3600)
                except asyncio.TimeoutError:
                    pass
                _pending_approvals.pop(approval_id, None)
                continue

            # ── Agent step: run LangGraph for this agent ──
            agent = step["agent"]
            await ws_manager.broadcast_node_started(execution_id, node_id, "agent", node_label)

            _executions[execution_id].setdefault("steps", []).append({
                "node_id": node_id, "agent": agent, "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
            })

            # Run graph up to current agent step
            initial_state["current_step"] = agent_step_idx
            try:
                final_state = await governance_graph.ainvoke(initial_state, config)
                agent_results = final_state.get("agent_results", {})
                result = agent_results.get(agent, {})
            except Exception as e:
                logger.error(f"[Engine] Graph error for {agent}: {e}")
                result = {"output": {"error": str(e)}, "metrics": {}}

            metrics = result.get("metrics", {})
            output_data = result.get("output", {})

            # Mark step complete
            for s in _executions[execution_id]["steps"]:
                if s.get("agent") == agent and s["status"] == "running":
                    s["status"] = "completed"
                    s["completed_at"] = datetime.now(timezone.utc).isoformat()
                    s["metrics"] = metrics
                    s["output"] = output_data
                    break

            await ws_manager.broadcast_node_completed(execution_id, node_id, output_data, {
                "execution_time_ms": metrics.get("execution_time_ms", 0),
                "token_usage": metrics.get("token_usage", 0),
                "cost_cents": metrics.get("cost_cents", 0),
                "confidence": metrics.get("confidence", 0),
            })

            # Update initial state for next iteration
            initial_state = final_state
            agent_step_idx += 1

            # Small delay for demo
            await asyncio.sleep(0.3)

        # ── Aggregate final results ──
        final_output = _aggregate(initial_state.get("agent_results", {}), full_plan, _executions[execution_id]["steps"])

        _executions[execution_id]["status"] = "completed"
        _executions[execution_id]["completed_at"] = datetime.now(timezone.utc)
        _executions[execution_id]["output"] = final_output

        await ws_manager.broadcast_workflow_completed(execution_id, final_output)
        logger.info(f"[Engine] Execution {execution_id} completed")

        return {"execution_id": execution_id, "status": "completed", "output": final_output}

    except Exception as e:
        logger.error(f"[Engine] Execution {execution_id} failed: {e}", exc_info=True)
        _executions[execution_id]["status"] = "failed"
        _executions[execution_id]["error"] = str(e)
        await ws_manager.broadcast_workflow_failed(execution_id, str(e))
        return {"execution_id": execution_id, "status": "failed", "error": str(e)}


def _build_full_plan(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """Build execution plan including approval checkpoints."""
    node_map = {n["id"]: n for n in nodes}
    target_ids = {e.get("targetNodeId") for e in edges}
    roots = [n for n in nodes if n["id"] not in target_ids]

    visited: set[str] = set()
    queue = [n["id"] for n in roots]
    plan = []

    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        node = node_map.get(node_id)
        if not node:
            continue

        if node.get("nodeType") != "trigger":
            plan.append({
                "node_id": node_id,
                "node_label": node.get("label", ""),
                "agent": node.get("config", {}).get("agentType", node.get("nodeType", "")),
                "description": node.get("config", {}).get("description", ""),
                "requires_approval": node.get("nodeType") == "approval",
            })

        for edge in edges:
            if edge.get("sourceNodeId") == node_id:
                queue.append(edge.get("targetNodeId"))

    return plan


def _aggregate(agent_results: dict, plan: list[dict], steps: list[dict]) -> dict:
    """Build final execution summary."""
    findings = []
    total_tokens = 0
    total_cost = 0
    total_time = 0

    for step in plan:
        if step.get("requires_approval"):
            continue
        agent = step.get("agent", "")
        result = agent_results.get(agent, {})
        if result:
            m = result.get("metrics", {})
            findings.append({
                "agent": agent,
                "label": step.get("node_label", ""),
                "output": result.get("output", {}),
                "metrics": m,
            })
            total_tokens += m.get("token_usage", 0)
            total_cost += m.get("cost_cents", 0)
            total_time += m.get("execution_time_ms", 0)

    return {
        "status": "completed",
        "findings": findings,
        "summary": f"Executed {len(findings)} agent steps. Total: {total_tokens} tokens, ${total_cost/100:.2f}, {total_time}ms",
        "metrics": {
            "total_tokens": total_tokens,
            "total_cost_cents": total_cost,
            "total_execution_time_ms": total_time,
            "agents_executed": len(findings),
        },
    }


async def resolve_approval(approval_id: str, decision: str, reason: Optional[str] = None):
    if approval_id in _pending_approvals:
        _pending_approvals[approval_id].set()
        for exec_id, exec_data in _executions.items():
            for a in exec_data.get("approvals", []):
                if a.get("approval_id") == approval_id:
                    a["status"] = "approved" if decision == "approved" else "rejected"
                    a["resolved_at"] = datetime.now(timezone.utc).isoformat()
                    a["reason"] = reason
                    await ws_manager.broadcast(exec_id, "approval.responded", {
                        "approval_id": approval_id, "decision": decision, "reason": reason,
                    })
                    return True
    return False


def get_execution(execution_id: str) -> Optional[dict]:
    return _executions.get(execution_id)


def get_pending_approvals() -> list[dict]:
    pending = []
    for exec_data in _executions.values():
        for a in exec_data.get("approvals", []):
            if a.get("status") == "pending":
                pending.append({**a, "execution_id": exec_data["id"]})
    return pending
