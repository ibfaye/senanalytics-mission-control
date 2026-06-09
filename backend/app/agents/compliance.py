"""
Compliance Agent — maps data assets to regulatory frameworks:
GDPR, CDP (Senegal Data Protection Act), PIPEDA, SOC2, ISO 27001.
Flags compliance gaps and produces evidence.
"""

import logging
from typing import Any
from app.agents.helpers import run_agent

logger = logging.getLogger(__name__)

COMPLIANCE_SYSTEM_PROMPT = """You are the Compliance Agent for Sen'Analytics Mission Control.
Your job is to map data assets to regulatory frameworks (GDPR, CDP Senegal, PIPEDA,
SOC2, ISO 27001). Identify compliance gaps, assign severity levels, and reference
specific articles/controls.

Return a JSON object with:
- frameworks: {name: {status, gaps, score}}
- gaps: array of {framework, article, description, severity, affected_data}"""

_DEMO_OUTPUT = {
    "frameworks": {
        "GDPR": {"status": "PARTIALLY_COMPLIANT", "gaps": 3, "score": 0.78},
        "CDP_SENEGAL": {"status": "NON_COMPLIANT", "gaps": 5, "score": 0.55},
        "PIPEDA": {"status": "PARTIALLY_COMPLIANT", "gaps": 2, "score": 0.85},
        "SOC2": {"status": "PARTIALLY_COMPLIANT", "gaps": 4, "score": 0.72},
        "ISO27001": {"status": "NON_COMPLIANT", "gaps": 7, "score": 0.48},
    },
    "gaps": [
        {"framework": "GDPR", "article": "Art. 32", "description": "Security of processing — PII encryption missing", "severity": "HIGH", "affected_data": ["customers.PII"]},
        {"framework": "CDP_SENEGAL", "article": "CDP-ART-34", "description": "PII encryption at rest requirement", "severity": "CRITICAL", "affected_data": ["customers.email", "customers.phone"]},
        {"framework": "CDP_SENEGAL", "article": "CDP-ART-49", "description": "Cross-border transfer authorization", "severity": "HIGH", "affected_data": ["analytics_warehouse"]},
        {"framework": "SOC2", "control": "CC6.1", "description": "Logical access controls", "severity": "MEDIUM", "affected_data": ["marketing_crm"]},
    ],
}

_DEMO_METRICS = {"execution_time_ms": 750, "token_usage": 610, "cost_cents": 2, "confidence": 0.91}


async def compliance_node(state: dict[str, Any]) -> dict[str, Any]:
    """Map data assets to regulatory frameworks, identify gaps."""
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Compliance] Mapping compliance: {task_context.get('description', '')}")

    result = await run_agent(
        agent_name="compliance",
        system_prompt=COMPLIANCE_SYSTEM_PROMPT,
        task_context=task_context,
        agent_results=agent_results,
        simulated_output=_DEMO_OUTPUT,
        simulated_metrics=_DEMO_METRICS,
    )

    agent_results["compliance"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
