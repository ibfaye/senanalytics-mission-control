"""
Supervisor Agent — plans and routes work to specialized agents.
Approval checkpoints are handled externally by the execution engine.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def supervisor_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    LangGraph node: Supervisor routes to the next agent in the plan.

    The plan is pre-populated by the execution engine. The supervisor
    checks whether execution is complete and routes to the next agent.
    When all steps are done, it aggregates final output.
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    agent_results = state.get("agent_results", {})

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
