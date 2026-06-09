"""
Risk Agent — scores and prioritizes risks based on likelihood and impact.
Produces risk heatmaps and remediation priorities.
"""

import logging
from typing import Any
from app.agents.helpers import run_agent

logger = logging.getLogger(__name__)

RISK_SYSTEM_PROMPT = """You are the Risk Agent for Sen'Analytics Mission Control.
Your job is to score and prioritize risks: likelihood × impact = risk score.
Produce a prioritized remediation plan with clear deadlines.

Return a JSON object with:
- risks: array of {id, name, likelihood, impact, score, severity, remediation_priority}
- risk_distribution: {critical, high, medium, low}
- remediation_plan: array of priority-ordered action strings"""

_DEMO_OUTPUT = {
    "risks": [
        {"id": "RISK-001", "name": "Unencrypted PII exposure", "likelihood": 0.8, "impact": 0.9, "score": 0.72, "severity": "CRITICAL", "remediation_priority": 1},
        {"id": "RISK-002", "name": "Cross-border data transfer violation", "likelihood": 0.6, "impact": 0.85, "score": 0.51, "severity": "HIGH", "remediation_priority": 2},
        {"id": "RISK-003", "name": "Overly permissive IAM", "likelihood": 0.5, "impact": 0.7, "score": 0.35, "severity": "MEDIUM", "remediation_priority": 3},
    ],
    "risk_distribution": {"critical": 1, "high": 1, "medium": 1, "low": 0},
    "remediation_plan": [
        "1. Enable TDE on customer-db-prod-01 (CRITICAL)",
        "2. Submit cross-border transfer authorization to CDP (HIGH)",
        "3. Apply least-privilege IAM policy (MEDIUM)",
    ],
}

_DEMO_METRICS = {"execution_time_ms": 520, "token_usage": 410, "cost_cents": 1, "confidence": 0.87}


async def risk_node(state: dict[str, Any]) -> dict[str, Any]:
    """Score and prioritize risks: likelihood × impact = risk score."""
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Risk] Scoring risks: {task_context.get('description', '')}")

    result = await run_agent(
        agent_name="risk",
        system_prompt=RISK_SYSTEM_PROMPT,
        task_context=task_context,
        agent_results=agent_results,
        simulated_output=_DEMO_OUTPUT,
        simulated_metrics=_DEMO_METRICS,
    )

    agent_results["risk"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
