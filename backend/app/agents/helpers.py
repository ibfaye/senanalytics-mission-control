"""
Agent helpers — shared utilities for LLM-powered governance agents.
Each agent uses run_agent() to call the LLM with structured prompts.
Falls back to simulated data when LLM is not configured.
"""

import logging
from typing import Any
from app.core.llm_client import llm

logger = logging.getLogger(__name__)


async def run_agent(
    agent_name: str,
    system_prompt: str,
    task_context: dict[str, Any],
    agent_results: dict[str, Any],
    simulated_output: dict[str, Any],
    simulated_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run an agent step: call the LLM if configured, otherwise return simulated data.

    Args:
        agent_name: e.g. "discovery", "classification"
        system_prompt: The agent's system prompt
        task_context: Current task context from the engine (action, description, agent)
        agent_results: Accumulated results from previous agents
        simulated_output: Output to return when LLM is not configured
        simulated_metrics: Metrics to return when LLM is not configured

    Returns:
        {"output": {...}, "metrics": {...}, "agent_type": "..."}
    """
    if not llm.is_configured:
        return _simulated_result(agent_name, simulated_output, simulated_metrics or {})

    # Build user prompt from task context + prior results
    prior_results_summary = _summarize_prior_results(agent_results)
    user_prompt = f"""Task: {task_context.get('action', task_context.get('description', ''))}

Context: {task_context.get('description', '')}

Prior agent results:
{prior_results_summary if prior_results_summary else 'None (this is the first agent in the pipeline)'}

Return your findings as a JSON object."""

    try:
        llm_result = await llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )

        output = llm_result.get("parsed") or {"raw": llm_result["content"]}
        metrics = {
            "execution_time_ms": llm_result["duration_ms"],
            "token_usage": llm_result["tokens"]["total"],
            "cost_cents": llm_result["cost_cents"],
            "confidence": 0.88,
        }

        return {
            "output": output,
            "metrics": metrics,
            "agent_type": agent_name,
            "model": llm_result["model"],
        }

    except Exception as e:
        logger.error(f"[{agent_name}] LLM call failed: {e}. Falling back to simulated data.")
        return _simulated_result(
            agent_name, simulated_output, simulated_metrics or {},
            error=str(e),
        )


def _simulated_result(
    agent_name: str,
    output: dict[str, Any],
    metrics: dict[str, Any],
    error: str | None = None,
) -> dict[str, Any]:
    """Return simulated demo data (used when LLM is unavailable)."""
    result: dict[str, Any] = {
        "output": output,
        "metrics": metrics or {
            "execution_time_ms": 450,
            "token_usage": 320,
            "cost_cents": 1,
            "confidence": 0.95,
        },
        "agent_type": agent_name,
    }
    if error:
        result["fallback_reason"] = error
    return result


def _summarize_prior_results(agent_results: dict[str, Any]) -> str:
    """Build a concise summary of what previous agents found."""
    if not agent_results:
        return ""
    lines = []
    for name, result in agent_results.items():
        output = result.get("output", {})
        if isinstance(output, dict):
            # Pick key fields for context
            keys = list(output.keys())[:5]
            summary = {k: output[k] for k in keys if not isinstance(output[k], (list, dict))}
            if summary:
                lines.append(f"- {name}: {summary}")
    return "\n".join(lines) if lines else ""
