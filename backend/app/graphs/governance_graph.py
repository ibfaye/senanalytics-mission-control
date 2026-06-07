"""
LangGraph StateGraph — supervisor-worker pattern for governance workflows.
Supervisor plans + routes; workers execute; engine handles approvals externally.
"""

import logging
from typing import Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional

from app.agents.supervisor import supervisor_node
from app.agents.discovery import discovery_node
from app.agents.classification import classification_node
from app.agents.security import security_node
from app.agents.compliance import compliance_node
from app.agents.risk import risk_node
from app.agents.reporting import reporting_node

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    """Shared state across all LangGraph nodes."""
    messages: list[dict]
    task: str
    workflow_id: str
    execution_id: str
    workflow_nodes: list[dict]
    workflow_edges: list[dict]
    plan: list[dict]
    current_step: int
    agent_results: dict[str, Any]
    next_agent: str
    current_task_context: dict
    final_output: Optional[dict]
    errors: list[str]


# ── Router ──

def route_after_supervisor(state: AgentState) -> Literal[
    "discovery", "classification", "security", "compliance",
    "risk", "reporting", "END"
]:
    """Route to next worker or END."""
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])

    if current_step >= len(plan):
        return "END"

    next_agent = plan[current_step].get("agent", "")
    if next_agent in ("discovery", "classification", "security", "compliance", "risk", "reporting"):
        return next_agent  # type: ignore
    return "END"


# ── Build graph ──

def build_governance_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("discovery", discovery_node)
    builder.add_node("classification", classification_node)
    builder.add_node("security", security_node)
    builder.add_node("compliance", compliance_node)
    builder.add_node("risk", risk_node)
    builder.add_node("reporting", reporting_node)

    builder.set_entry_point("supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "discovery": "discovery",
            "classification": "classification",
            "security": "security",
            "compliance": "compliance",
            "risk": "risk",
            "reporting": "reporting",
            "END": END,
        },
    )

    builder.add_edge("discovery", "supervisor")
    builder.add_edge("classification", "supervisor")
    builder.add_edge("security", "supervisor")
    builder.add_edge("compliance", "supervisor")
    builder.add_edge("risk", "supervisor")
    builder.add_edge("reporting", "supervisor")

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    logger.info("[Graph] Governance graph compiled with 8 nodes")
    return graph


governance_graph = build_governance_graph()
