"""Agents API — list available agents and their capabilities."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/agents", tags=["agents"])


BUILTIN_AGENTS = [
    {
        "id": "agent-supervisor",
        "name": "supervisor",
        "displayName": "Supervisor Agent",
        "agentType": "supervisor",
        "description": "Orchestrates workflow execution: plans, routes, delegates to specialized agents, manages approval checkpoints, and aggregates results.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-discovery",
        "name": "discovery",
        "displayName": "Discovery Agent",
        "agentType": "discovery",
        "description": "Discovers and catalogs data sources, analyzes schemas, extracts metadata from databases, data warehouses, and lakes.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-classification",
        "name": "classification",
        "displayName": "Classification Agent",
        "agentType": "classification",
        "description": "Detects and classifies PII, PHI, SPI, and other sensitive data types across all registered data sources.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-security",
        "name": "security",
        "displayName": "Security Agent",
        "agentType": "security",
        "description": "Reviews security posture, evaluates IAM policies, identifies vulnerabilities, and assesses encryption configurations.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-compliance",
        "name": "compliance",
        "displayName": "Compliance Agent",
        "agentType": "compliance",
        "description": "Maps data assets to regulatory frameworks: GDPR, CDP (Senegal), PIPEDA, SOC2, ISO 27001. Flags compliance gaps.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-risk",
        "name": "risk",
        "displayName": "Risk Agent",
        "agentType": "risk",
        "description": "Scores and prioritizes risks based on likelihood and impact. Produces risk heatmaps and remediation priorities.",
        "isActive": True,
        "tools": [],
    },
    {
        "id": "agent-reporting",
        "name": "reporting",
        "displayName": "Reporting Agent",
        "agentType": "reporting",
        "description": "Generates executive summaries, audit reports, compliance documentation, and detailed remediation plans.",
        "isActive": True,
        "tools": [],
    },
]


@router.get("/")
async def list_agents():
    return BUILTIN_AGENTS


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    for agent in BUILTIN_AGENTS:
        if agent["id"] == agent_id or agent["name"] == agent_id:
            return agent
    return None
