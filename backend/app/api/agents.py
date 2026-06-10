"""Agents API — CRUD for governance agents."""

import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


# ── Pydantic Models ────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: str
    displayName: str
    agentType: str
    description: str = ""
    systemPrompt: str | None = None
    modelProvider: str | None = None
    modelName: str | None = None
    tools: list[str] = []


class AgentUpdate(BaseModel):
    displayName: str | None = None
    description: str | None = None
    systemPrompt: str | None = None
    modelProvider: str | None = None
    modelName: str | None = None
    tools: list[str] | None = None
    isActive: bool | None = None


# ── In-memory store (seeded with builtins) ─────────────────────

_agents_store: list[dict] = []
_seeded = False


def _ensure_seeded():
    global _seeded, _agents_store
    if _seeded:
        return
    _agents_store = [
        {"id": "agent-supervisor", "name": "supervisor", "displayName": "Supervisor Agent",
         "agentType": "supervisor", "description": "Orchestrates workflow execution: plans, routes, delegates.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-discovery", "name": "discovery", "displayName": "Discovery Agent",
         "agentType": "discovery", "description": "Discovers and catalogs data sources, analyzes schemas.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-classification", "name": "classification", "displayName": "Classification Agent",
         "agentType": "classification", "description": "Detects PII, PHI, SPI and sensitive data types.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-security", "name": "security", "displayName": "Security Agent",
         "agentType": "security", "description": "Reviews security posture, IAM, vulnerabilities.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-compliance", "name": "compliance", "displayName": "Compliance Agent",
         "agentType": "compliance", "description": "Maps to GDPR, CDP, PIPEDA, SOC2, ISO 27001.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-risk", "name": "risk", "displayName": "Risk Agent",
         "agentType": "risk", "description": "Scores and prioritizes risks, produces heatmaps.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
        {"id": "agent-reporting", "name": "reporting", "displayName": "Reporting Agent",
         "agentType": "reporting", "description": "Generates executive summaries, audit reports.",
         "systemPrompt": None, "modelProvider": None, "modelName": None, "isActive": True, "tools": [],
         "createdAt": "2026-06-01T00:00:00Z", "updatedAt": "2026-06-01T00:00:00Z"},
    ]
    _seeded = True


# ── GET /api/agents ────────────────────────────────────────────

@router.get("")
async def list_agents():
    _ensure_seeded()
    if db.is_connected:
        rows = await db.fetch(
            """SELECT id, name, display_name, agent_type, description,
                      system_prompt, model_provider, model_name, is_active, config,
                      created_at, updated_at
               FROM agents ORDER BY name"""
        )
        if rows:
            return [_db_agent_to_dict(r) for r in rows]

    return _agents_store


# ── GET /api/agents/{agent_id} ─────────────────────────────────

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    _ensure_seeded()
    for agent in _agents_store:
        if agent["id"] == agent_id or agent["name"] == agent_id:
            return agent
    raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


# ── POST /api/agents ───────────────────────────────────────────

@router.post("", status_code=201)
async def create_agent(body: AgentCreate):
    _ensure_seeded()
    now = datetime.now(timezone.utc).isoformat()

    new_agent = {
        "id": f"agent-{uuid.uuid4().hex[:8]}",
        "name": body.name,
        "displayName": body.displayName,
        "agentType": body.agentType,
        "description": body.description,
        "systemPrompt": body.systemPrompt,
        "modelProvider": body.modelProvider,
        "modelName": body.modelName,
        "isActive": True,
        "tools": body.tools,
        "createdAt": now,
        "updatedAt": now,
    }

    if db.is_connected:
        import json
        await db.execute(
            """INSERT INTO agents (id, name, display_name, agent_type, description,
               system_prompt, model_provider, model_name, is_active, config, created_at, updated_at)
               VALUES ($1::uuid, $2, $3, $4::agent_type, $5, $6, $7, $8, $9, $10::jsonb, $11, $11)""",
            new_agent["id"], body.name, body.displayName, body.agentType,
            body.description, body.systemPrompt, body.modelProvider, body.modelName,
            True, json.dumps({"tools": body.tools}), now,
        )

    _agents_store.append(new_agent)
    logger.info(f"[Agents] Created: {body.name} ({new_agent['id']})")
    return new_agent


# ── PUT /api/agents/{agent_id} ─────────────────────────────────

@router.put("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate):
    _ensure_seeded()
    agent = None
    for a in _agents_store:
        if a["id"] == agent_id or a["name"] == agent_id:
            agent = a
            break

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = body.model_dump(exclude_unset=True)

    for key, value in updates.items():
        camel_key = key[:1].lower() + key[1:] if key[0].isupper() else key
        if camel_key in agent:
            agent[camel_key] = value
    agent["updatedAt"] = now

    if db.is_connected:
        import json
        set_clauses = []
        params: list = []
        idx = 1
        for key, value in updates.items():
            if key == "displayName":
                set_clauses.append(f"display_name = ${idx}"); params.append(value); idx += 1
            elif key == "description":
                set_clauses.append(f"description = ${idx}"); params.append(value); idx += 1
            elif key == "systemPrompt":
                set_clauses.append(f"system_prompt = ${idx}"); params.append(value); idx += 1
            elif key == "modelProvider":
                set_clauses.append(f"model_provider = ${idx}"); params.append(value); idx += 1
            elif key == "modelName":
                set_clauses.append(f"model_name = ${idx}"); params.append(value); idx += 1
            elif key == "isActive":
                set_clauses.append(f"is_active = ${idx}"); params.append(value); idx += 1
            elif key == "tools":
                set_clauses.append(f"config = jsonb_set(config, '{{tools}}', ${idx}::jsonb)")
                params.append(json.dumps(value)); idx += 1

        if set_clauses:
            set_clauses.append(f"updated_at = ${idx}")
            params.append(now); idx += 1
            params.append(agent_id)
            await db.execute(
                f"UPDATE agents SET {', '.join(set_clauses)} WHERE id = ${idx}::uuid",
                *params,
            )

    logger.info(f"[Agents] Updated: {agent['name']}")
    return agent


# ── DELETE /api/agents/{agent_id} ──────────────────────────────

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    _ensure_seeded()
    for i, agent in enumerate(_agents_store):
        if agent["id"] == agent_id or agent["name"] == agent_id:
            deleted = _agents_store.pop(i)
            if db.is_connected:
                await db.execute(
                    "DELETE FROM agents WHERE id = $1::uuid", agent_id,
                )
            logger.info(f"[Agents] Deleted: {deleted['name']}")
            return {"message": "Agent deleted", "agent_id": agent_id}

    raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


# ── Helpers ────────────────────────────────────────────────────

def _db_agent_to_dict(row: dict) -> dict:
    import json
    raw_config = row.get("config")
    if isinstance(raw_config, str):
        try:
            config = json.loads(raw_config)
        except (json.JSONDecodeError, TypeError):
            config = {}
    elif isinstance(raw_config, dict):
        config = raw_config
    else:
        config = {}
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "displayName": row["display_name"],
        "agentType": row["agent_type"],
        "description": row.get("description") or "",
        "systemPrompt": row.get("system_prompt"),
        "modelProvider": row.get("model_provider"),
        "modelName": row.get("model_name"),
        "isActive": row.get("is_active", True),
        "tools": config.get("tools", []),
        "createdAt": _iso(row.get("created_at")),
        "updatedAt": _iso(row.get("updated_at")),
    }


def _iso(val) -> str:
    if val is None:
        return ""
    return val.isoformat() if hasattr(val, "isoformat") else str(val)
