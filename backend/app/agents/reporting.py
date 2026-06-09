"""
Reporting Agent — generates executive summaries, audit reports,
compliance documentation, and remediation plans.
"""

import logging
from typing import Any
from app.agents.helpers import run_agent

logger = logging.getLogger(__name__)

REPORTING_SYSTEM_PROMPT = """You are the Reporting Agent for Sen'Analytics Mission Control.
Your job is to generate executive summaries, audit reports, compliance documentation,
and prioritized remediation plans based on the accumulated findings from all agents.

Return a JSON object with:
- reports: array of {type, title, summary/findings_count/items}"""

_DEMO_OUTPUT = {
    "reports": [
        {"type": "executive_summary", "title": "GDPR Compliance Audit — Executive Summary",
         "summary": "Audit of 3 data sources across 5 compliance frameworks. 1 CRITICAL finding (PII encryption), 2 HIGH findings. CDP Senegal compliance at 55% — immediate action required.",
         "generated_at": "2026-06-07T12:00:00Z"},
        {"type": "audit_report", "title": "Full Audit Trail",
         "findings_count": 6, "frameworks_checked": 5, "remediation_items": 3},
        {"type": "remediation_plan", "title": "Remediation Action Plan",
         "items": [
             {"priority": 1, "action": "Enable TDE on customer-db-prod-01", "deadline": "48h"},
             {"priority": 2, "action": "Submit CDP cross-border authorization", "deadline": "30 days"},
             {"priority": 3, "action": "Apply IAM least-privilege policy", "deadline": "7 days"},
         ]},
    ],
}

_DEMO_METRICS = {"execution_time_ms": 380, "token_usage": 290, "cost_cents": 1, "confidence": 0.93}


async def reporting_node(state: dict[str, Any]) -> dict[str, Any]:
    """Generate reports: executive summary, audit trail, remediation plan."""
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Reporting] Generating reports: {task_context.get('description', '')}")

    result = await run_agent(
        agent_name="reporting",
        system_prompt=REPORTING_SYSTEM_PROMPT,
        task_context=task_context,
        agent_results=agent_results,
        simulated_output=_DEMO_OUTPUT,
        simulated_metrics=_DEMO_METRICS,
    )

    agent_results["reporting"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
