"""
Discovery Agent — discovers and catalogs data sources, analyzes schemas,
extracts metadata from databases, data warehouses, and lakes.
"""

import logging
from typing import Any
from app.agents.helpers import run_agent

logger = logging.getLogger(__name__)

DISCOVERY_SYSTEM_PROMPT = """You are the Discovery Agent for Sen'Analytics Mission Control.
Your job is to discover and catalog data sources, analyze their schemas,
and extract metadata. You identify tables, columns, data types, relationships,
and data volumes across all connected systems.

Return your findings as a JSON object with these fields:
- data_sources_found: number of data sources discovered
- catalogs: array of {name, type, tables, total_rows, size_gb}
- schemas_discovered: array of {table, columns: [{name, type, potential_pii}]}"""

# Simulated fallback output
_DEMO_OUTPUT = {
    "data_sources_found": 3,
    "catalogs": [
        {"name": "customer_db", "type": "PostgreSQL", "tables": 12, "total_rows": 1500000, "size_gb": 2.4},
        {"name": "analytics_warehouse", "type": "Snowflake", "tables": 8, "total_rows": 5000000, "size_gb": 8.1},
        {"name": "marketing_crm", "type": "SQL Server", "tables": 5, "total_rows": 300000, "size_gb": 0.6},
    ],
    "schemas_discovered": [
        {"table": "customers", "columns": [
            {"name": "id", "type": "UUID"},
            {"name": "email", "type": "VARCHAR(255)", "potential_pii": True},
            {"name": "full_name", "type": "VARCHAR(255)", "potential_pii": True},
            {"name": "phone", "type": "VARCHAR(20)", "potential_pii": True},
            {"name": "address", "type": "TEXT", "potential_pii": True},
            {"name": "created_at", "type": "TIMESTAMP"},
        ]}
    ],
}

_DEMO_METRICS = {"execution_time_ms": 450, "token_usage": 320, "cost_cents": 1, "confidence": 0.95}


async def discovery_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Discover and catalog data sources. Calls LLM when configured,
    falls back to simulated demo data otherwise.
    """
    task_context = state.get("current_task_context", {})
    agent_results = state.get("agent_results", {})

    logger.info(f"[Discovery] Scanning data sources: {task_context.get('description', '')}")

    result = await run_agent(
        agent_name="discovery",
        system_prompt=DISCOVERY_SYSTEM_PROMPT,
        task_context=task_context,
        agent_results=agent_results,
        simulated_output=_DEMO_OUTPUT,
        simulated_metrics=_DEMO_METRICS,
    )

    agent_results["discovery"] = result
    state["agent_results"] = agent_results
    state["current_step"] = state.get("current_step", 0) + 1

    return state
