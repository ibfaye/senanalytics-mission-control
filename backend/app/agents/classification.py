"""
Classification Agent — detects and classifies PII, PHI, SPI,
and other sensitive data types across registered data sources.
"""

import logging
from typing import Any
from app.agents.helpers import run_agent

logger = logging.getLogger(__name__)

CLASSIFICATION_SYSTEM_PROMPT = """You are the Classification Agent for Sen'Analytics Mission Control.
Your job is to detect and classify PII, PHI, SPI, and other sensitive data types
across all registered data sources. You assign sensitivity levels (HIGH/MEDIUM/LOW)
and confidence scores to each finding.

Return a JSON object with:
- total_fields_scanned: number
- pii_fields_found: number
- findings: array of {field, classification, sensitivity, confidence}"""

_DEMO_OUTPUT = {
    "total_fields_scanned": 48,
    "pii_fields_found": 12,
    "findings": [
        {"field": "customers.email", "classification": "PII-EMAIL", "sensitivity": "HIGH", "confidence": 0.98},
        {"field": "customers.full_name", "classification": "PII-NAME", "sensitivity": "HIGH", "confidence": 0.99},
        {"field": "customers.phone", "classification": "PII-PHONE", "sensitivity": "HIGH", "confidence": 0.97},
        {"field": "customers.address", "classification": "PII-ADDRESS", "sensitivity": "MEDIUM", "confidence": 0.94},
        {"field": "analytics.ip_address", "classification": "PII-NETWORK", "sensitivity": "MEDIUM", "confidence": 0.91},
    ],
}

_DEMO_METRICS = {"execution_time_ms": 680, "token_usage": 540, "cost_cents": 2, "confidence": 0.96}


async def classification_node(state: dict[str, Any]) -> dict[str, Any]:
    """Classify sensitive data: PII detection, sensitivity labeling."""
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Classification] Detecting PII/sensitive data: {task_context.get('description', '')}")

    result = await run_agent(
        agent_name="classification",
        system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
        task_context=task_context,
        agent_results=agent_results,
        simulated_output=_DEMO_OUTPUT,
        simulated_metrics=_DEMO_METRICS,
    )

    agent_results["classification"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
