"""
Security Agent — reviews security posture, IAM policies, encryption,
vulnerabilities, and identifies security gaps.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def security_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Review security posture: IAM, encryption, vulnerabilities.
    """
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Security] Reviewing security posture: {task_context.get('description', '')}")

    result = {
        "output": {
            "findings": [
                {
                    "id": "SEC-001",
                    "severity": "CRITICAL",
                    "category": "encryption",
                    "description": "PII fields in customers table not encrypted at rest",
                    "affected_resources": ["customers.email", "customers.phone"],
                    "remediation": "Enable TDE on customer-db-prod-01",
                },
                {
                    "id": "SEC-002",
                    "severity": "HIGH",
                    "category": "iam",
                    "description": "Overly permissive IAM role on analytics pipeline",
                    "affected_resources": ["analytics_warehouse"],
                    "remediation": "Apply least-privilege policy to analytics-reader role",
                },
                {
                    "id": "SEC-003",
                    "severity": "MEDIUM",
                    "category": "network",
                    "description": "Marketing CRM accessible from public internet",
                    "affected_resources": ["marketing_crm"],
                    "remediation": "Restrict inbound to VPC only",
                },
            ],
            "summary": {
                "critical": 1,
                "high": 1,
                "medium": 1,
                "low": 0,
            },
        },
        "metrics": {
            "execution_time_ms": 920,
            "token_usage": 720,
            "cost_cents": 3,
            "confidence": 0.88,
        },
        "agent_type": "security",
    }

    agent_results["security"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
