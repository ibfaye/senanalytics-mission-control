"""
Supervisor Agent — plans and routes work to specialized agents.
Approval checkpoints are handled externally by the execution engine.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def supervisor_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    LangGraph node: Supervisor plans and routes work.

    - First call: creates plan from workflow nodes (excluding triggers + approvals)
    - Subsequent calls: routes to next agent in the plan
    - When all steps done: sets final output
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    agent_results = state.get("agent_results", {})

    # ── First call: create plan ──
    if not plan:
        nodes = state.get("workflow_nodes", [])
        edges = state.get("workflow_edges", [])
        plan = _build_plan(nodes, edges)
        state["plan"] = plan
        state["current_step"] = 0
        logger.info(f"[Supervisor] Created plan with {len(plan)} steps: {[s['agent'] for s in plan]}")
        return state

    # ── Check completion ──
    if current_step >= len(plan):
        state["final_output"] = _aggregate(agent_results, plan)
        logger.info("[Supervisor] All steps complete")
        return state

    # ── Route to next agent ──
    step = plan[current_step]
    next_agent = step.get("agent", "")

    state["next_agent"] = next_agent
    state["current_task_context"] = {
        "action": step.get("action", ""),
        "description": step.get("description", ""),
        "agent": next_agent,
    }

    logger.info(f"[Supervisor] Routing step {current_step} → {next_agent}")
    return state


def _build_plan(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """Build execution plan from workflow nodes (skip triggers + approvals)."""
    node_map = {n["id"]: n for n in nodes}
    target_ids = {e.get("targetNodeId") for e in edges}

    # BFS from root nodes
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

        # Skip trigger and approval nodes
        if node.get("nodeType") not in ("trigger", "approval"):
            plan.append({
                "node_id": node_id,
                "node_label": node.get("label", ""),
                "agent": node.get("config", {}).get("agentType", node.get("nodeType", "")),
                "action": f"Execute {node.get('label', 'task')}",
                "description": node.get("config", {}).get("description", ""),
            })

        for edge in edges:
            if edge.get("sourceNodeId") == node_id:
                queue.append(edge.get("targetNodeId"))

    return plan


def _aggregate(agent_results: dict, plan: list[dict]) -> dict:
    """Aggregate worker results."""
    findings = []
    for step in plan:
        agent = step.get("agent", "")
        result = agent_results.get(agent, {})
        if result:
            findings.append({
                "agent": agent,
                "label": step.get("node_label", ""),
                "output": result.get("output", {}),
            })

    return {
        "status": "completed",
        "findings": findings,
        "summary": f"Executed {len(findings)} agent steps successfully.",
    }
