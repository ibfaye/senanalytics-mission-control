"""
Execution Engine — runs workflows with live WebSocket streaming.
Agent nodes are called directly by the engine loop; WebSocket events
are broadcast between steps for live canvas animation.
"""

import asyncio
import logging
import uuid
from collections import deque
from typing import Optional, Any
from datetime import datetime, timezone

from app.core.websocket import ws_manager
from app.core.persistence import save_execution, update_execution_status, save_step, update_step

# ── Agent registry: name → async node function ──
from app.agents.discovery import discovery_node
from app.agents.classification import classification_node
from app.agents.security import security_node
from app.agents.compliance import compliance_node
from app.agents.risk import risk_node
from app.agents.reporting import reporting_node

_AGENT_REGISTRY: dict[str, Any] = {
    "discovery": discovery_node,
    "classification": classification_node,
    "security": security_node,
    "compliance": compliance_node,
    "risk": risk_node,
    "reporting": reporting_node,
}

logger = logging.getLogger(__name__)

_executions: dict[str, dict] = {}
_pending_approvals: dict[str, asyncio.Event] = {}


async def _broadcast_to_all(execution_id: str, workflow_id: str, event: str, data: dict):
    """Broadcast an event to both the execution channel and the workflow channel.

    The frontend connects via workflow_id (from the URL), but the engine
    generates a unique execution_id per run. Broadcasting to both ensures
    the frontend always receives events regardless of which channel it's on.
    """
    await ws_manager.broadcast(execution_id, event, data)
    await ws_manager.broadcast(workflow_id, event, data)


async def execute_workflow(
    workflow_id: str,
    workflow_nodes: list[dict],
    workflow_edges: list[dict],
    task: str = "Execute governance workflow",
    input_data: Optional[dict] = None,
) -> dict:
    """
    Execute workflow: walk the plan, call agents directly, broadcast live events,
    handle approval checkpoints.
    """
    execution_id = str(uuid.uuid4())
    _executions[execution_id] = {
        "id": execution_id, "workflow_id": workflow_id, "status": "running",
        "started_at": datetime.now(timezone.utc), "completed_at": None,
        "steps": [], "output": None, "error": None,
    }

    logger.info(f"[Engine] Starting execution {execution_id}")

    await _broadcast_to_all(execution_id, workflow_id, "workflow.execution.started", {
        "executionId": execution_id, "workflowId": workflow_id, "workflowName": task,
    })

    # Persist execution to PostgreSQL
    await save_execution(execution_id, workflow_id, "running")

    full_plan = _build_full_plan(workflow_nodes, workflow_edges)
    agent_plan = [s for s in full_plan if not s.get("requires_approval")]
    logger.info(f"[Engine] Plan: {len(full_plan)} steps ({len(agent_plan)} agent steps)")

    # Shared state passed to agent nodes (accumulates results across steps)
    state: dict[str, Any] = {
        "task": task,
        "workflow_id": workflow_id,
        "execution_id": execution_id,
        "agent_results": {},
        "current_task_context": {},
        "errors": [],
    }

    try:
        # Pause/resume support
        _executions[execution_id]["_pause_event"] = asyncio.Event()
        _executions[execution_id]["_pause_event"].set()  # start unpaused
        _executions[execution_id]["_cancelled"] = False

        agent_step_idx = 0

        for step in full_plan:
            # ── Check for cancellation ──
            if _executions[execution_id].get("_cancelled"):
                logger.info(f"[Engine] Execution {execution_id} cancelled")
                _executions[execution_id]["status"] = "cancelled"
                await _broadcast_to_all(execution_id, workflow_id, "workflow.execution.failed", {
                    "executionId": execution_id,
                    "error": "Execution cancelled by user",
                })
                return {"execution_id": execution_id, "status": "cancelled", "error": "Cancelled by user"}

            # ── Wait if paused ──
            pause_evt = _executions[execution_id].get("_pause_event")
            if pause_evt:
                await pause_evt.wait()
            node_id = step["node_id"]
            node_label = step["node_label"]

            # ── Approval step ──
            if step.get("requires_approval"):
                approval_id = str(uuid.uuid4())
                # Build context with accumulated agent results for review
                agent_results = state.get("agent_results", {})
                context_summary = {}
                for agent_name, result in agent_results.items():
                    output = result.get("output", {})
                    if isinstance(output, dict):
                        # Extract key metrics/summaries
                        if "findings" in output:
                            context_summary[agent_name] = {
                                "findings_count": len(output["findings"]),
                                "summary": output["findings"][:3] if output["findings"] else [],
                            }
                        elif "data_sources_found" in output:
                            context_summary[agent_name] = {
                                "data_sources": output["data_sources_found"],
                                "catalogs": [c["name"] for c in output.get("catalogs", [])[:3]],
                            }
                        elif "total_fields_scanned" in output:
                            context_summary[agent_name] = {
                                "fields_scanned": output["total_fields_scanned"],
                                "pii_found": output["pii_fields_found"],
                            }
                        else:
                            context_summary[agent_name] = {"keys": list(output.keys())[:5]}
                await _broadcast_to_all(execution_id, workflow_id, "approval.requested", {
                    "executionId": execution_id,
                    "approvalId": approval_id, "nodeId": node_id,
                    "nodeLabel": node_label,
                    "reason": step.get("description", "Human approval required"),
                    "context": context_summary,
                })
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

            # ── Agent step: call agent function directly ──
            agent = step["agent"]
            agent_fn = _AGENT_REGISTRY.get(agent)
            if not agent_fn:
                logger.warning(f"[Engine] Unknown agent '{agent}', skipping")
                continue

            await _broadcast_to_all(execution_id, workflow_id, "node.started", {
                "executionId": execution_id,
                "nodeId": node_id,
                "nodeType": "agent",
                "nodeLabel": node_label,
            })

            step_record = {
                "node_id": node_id, "agent": agent, "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
            _executions[execution_id].setdefault("steps", []).append(step_record)

            # Persist step to PostgreSQL
            await save_step(execution_id, agent_step_idx, node_id, agent)

            # Set context for the agent to read
            state["current_task_context"] = {
                "agent": agent,
                "description": step.get("description", ""),
                "action": f"Execute {node_label}",
            }

            failed = False
            result: dict = {}
            try:
                # Call agent node directly — returns updated state dict
                state = await agent_fn(state)
                result = state.get("agent_results", {}).get(agent, {})
            except Exception as e:
                logger.error(f"[Engine] Agent {agent} failed: {e}")
                result = {"output": {"error": str(e)}, "metrics": {}}
                failed = True
                state.setdefault("errors", []).append({"agent": agent, "error": str(e)})

                await _broadcast_to_all(execution_id, workflow_id, "node.failed", {
                    "executionId": execution_id,
                    "nodeId": node_id,
                    "error": str(e),
                    "retryable": True,
                })

            metrics = result.get("metrics", {})
            output_data = result.get("output", {})

            # Update step record
            step_record["status"] = "failed" if failed else "completed"
            step_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            step_record["metrics"] = metrics
            step_record["output"] = output_data

            # Persist step completion to PostgreSQL
            await update_step(
                execution_id, agent_step_idx,
                status="failed" if failed else "completed",
                execution_time_ms=metrics.get("execution_time_ms", 0),
                token_usage=metrics.get("token_usage", 0),
                cost_cents=metrics.get("cost_cents", 0),
                confidence_score=metrics.get("confidence", 0),
                output=output_data if not failed else None,
                error_message=str(e) if failed else None,
            )

            if not failed:
                await _broadcast_to_all(execution_id, workflow_id, "node.completed", {
                    "executionId": execution_id,
                    "nodeId": node_id,
                    "output": output_data,
                    "metrics": {
                        "executionTimeMs": metrics.get("execution_time_ms", 0),
                        "tokenUsage": metrics.get("token_usage", 0),
                        "costCents": metrics.get("cost_cents", 0),
                        "confidence": metrics.get("confidence", 0),
                    },
                })

            agent_step_idx += 1
            await asyncio.sleep(0.3)

        # ── Aggregate final results ──
        final_output = _aggregate(state.get("agent_results", {}), full_plan, _executions[execution_id]["steps"])

        _executions[execution_id]["status"] = "completed"
        _executions[execution_id]["completed_at"] = datetime.now(timezone.utc)
        _executions[execution_id]["output"] = final_output

        # Persist execution completion to PostgreSQL
        summary_metrics = final_output.get("metrics", {})
        await update_execution_status(
            execution_id, "completed",
            output=final_output,
            total_tokens=summary_metrics.get("total_tokens", 0),
            total_cost_cents=summary_metrics.get("total_cost_cents", 0),
            duration_ms=summary_metrics.get("total_execution_time_ms", 0),
        )

        await _broadcast_to_all(execution_id, workflow_id, "workflow.execution.completed", {
            "executionId": execution_id,
            "output": final_output,
        })
        logger.info(f"[Engine] Execution {execution_id} completed")

        return {"execution_id": execution_id, "status": "completed", "output": final_output}

    except Exception as e:
        logger.error(f"[Engine] Execution {execution_id} failed: {e}", exc_info=True)
        _executions[execution_id]["status"] = "failed"
        _executions[execution_id]["error"] = str(e)
        await update_execution_status(execution_id, "failed", error_message=str(e))
        await _broadcast_to_all(execution_id, workflow_id, "workflow.execution.failed", {
            "executionId": execution_id,
            "error": str(e),
        })
        return {"execution_id": execution_id, "status": "failed", "error": str(e)}


def _build_full_plan(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """Build execution plan including approval checkpoints (BFS, O(V+E))."""
    node_map = {n["id"]: n for n in nodes}
    target_ids = {e.get("targetNodeId") for e in edges}
    roots = [n for n in nodes if n["id"] not in target_ids]

    visited: set[str] = set()
    queue: deque[str] = deque(n["id"] for n in roots)
    plan: list[dict] = []

    while queue:
        node_id = queue.popleft()
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
                    await _broadcast_to_all(exec_id, exec_data.get("workflow_id", exec_id), "approval.responded", {
                        "approvalId": approval_id, "decision": decision, "reason": reason,
                    })
                    return True
    return False


def pause_execution(execution_id: str) -> bool:
    """Pause a running execution. The engine loop waits on an asyncio.Event."""
    exec_data = _executions.get(execution_id)
    if not exec_data or exec_data["status"] != "running":
        return False
    exec_data["status"] = "paused"
    pause_evt = exec_data.get("_pause_event")
    if pause_evt:
        pause_evt.clear()
    logger.info(f"[Engine] Execution {execution_id} paused")
    return True


def resume_execution(execution_id: str) -> bool:
    """Resume a paused execution."""
    exec_data = _executions.get(execution_id)
    if not exec_data or exec_data["status"] != "paused":
        return False
    exec_data["status"] = "running"
    pause_evt = exec_data.get("_pause_event")
    if pause_evt:
        pause_evt.set()
    logger.info(f"[Engine] Execution {execution_id} resumed")
    return True


def cancel_execution(execution_id: str) -> bool:
    """Cancel a running or paused execution."""
    exec_data = _executions.get(execution_id)
    if not exec_data or exec_data["status"] not in ("running", "paused"):
        return False
    exec_data["_cancelled"] = True
    # Unpause to let the loop see the cancellation
    pause_evt = exec_data.get("_pause_event")
    if pause_evt and exec_data["status"] == "paused":
        pause_evt.set()
        exec_data["status"] = "running"
    logger.info(f"[Engine] Execution {execution_id} cancel requested")
    return True


def get_execution(execution_id: str) -> Optional[dict]:
    return _executions.get(execution_id)


def get_pending_approvals() -> list[dict]:
    pending = []
    for exec_data in _executions.values():
        for a in exec_data.get("approvals", []):
            if a.get("status") == "pending":
                pending.append({**a, "execution_id": exec_data["id"]})
    return pending
