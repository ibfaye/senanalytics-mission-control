"""
Execution Persistence — saves workflow executions and steps to PostgreSQL.
Works alongside the in-memory engine; persists for audit trail.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional
from app.core.database import db

logger = logging.getLogger(__name__)

# PostgreSQL auto-generates UUIDs via DEFAULT gen_random_uuid()
# We only insert non-ID columns and let PG handle IDs


async def save_execution(execution_id: str, workflow_id: str,
                         status: str = "running", triggered_by: str = "system") -> bool:
    """Insert a new execution record into PostgreSQL."""
    if not db.is_connected:
        return False

    try:
        await db.execute(
            """INSERT INTO workflow_executions (id, workflow_id, status, triggered_by, started_at)
               VALUES ($1, $2, $3, $4, $5)""",
            execution_id, workflow_id, status, triggered_by,
            datetime.now(timezone.utc),
        )
        return True
    except Exception as e:
        logger.warning(f"[DB] save_execution: {e}")
        return False


async def update_execution_status(execution_id: str, status: str,
                                  output: Optional[dict] = None,
                                  error_message: Optional[str] = None,
                                  total_tokens: int = 0,
                                  total_cost_cents: int = 0,
                                  duration_ms: int = 0) -> bool:
    """Update an execution record on completion/failure."""
    if not db.is_connected:
        return False

    try:
        output_json = json.dumps(output) if output else None
        await db.execute(
            """UPDATE workflow_executions
               SET status = $1, output = $2::jsonb, error_message = $3,
                   total_tokens = $4, total_cost_cents = $5,
                   duration_ms = $6, completed_at = $7
               WHERE id = $8""",
            status, output_json, error_message,
            total_tokens, total_cost_cents,
            duration_ms, datetime.now(timezone.utc),
            execution_id,
        )
        return True
    except Exception as e:
        logger.warning(f"[DB] update_execution_status: {e}")
        return False


async def save_step(execution_id: str, step_order: int, node_id: str,
                    agent_id: str, step_type: str = "agent_call",
                    status: str = "running") -> bool:
    """Insert an execution step record."""
    if not db.is_connected:
        return False

    try:
        import uuid
        step_id = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO execution_steps (id, execution_id, step_order, node_id, agent_id, step_type, status, started_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            step_id, execution_id, step_order, node_id, agent_id,
            step_type, status, datetime.now(timezone.utc),
        )
        return True
    except Exception as e:
        logger.warning(f"[DB] save_step: {e}")
        return False


async def update_step(execution_id: str, step_order: int,
                      status: str = "completed",
                      execution_time_ms: int = 0,
                      token_usage: int = 0,
                      cost_cents: int = 0,
                      confidence_score: float = 0.0,
                      output: Optional[dict] = None,
                      error_message: Optional[str] = None) -> bool:
    """Update an execution step on completion."""
    if not db.is_connected:
        return False

    try:
        output_json = json.dumps(output) if output else None
        await db.execute(
            """UPDATE execution_steps
               SET status = $1, completed_at = $2, execution_time_ms = $3,
                   token_usage = $4, cost_cents = $5, confidence_score = $6,
                   output = $7::jsonb, error_message = $8
               WHERE execution_id = $9 AND step_order = $10""",
            status, datetime.now(timezone.utc), execution_time_ms,
            token_usage, cost_cents, confidence_score,
            output_json, error_message,
            execution_id, step_order,
        )
        return True
    except Exception as e:
        logger.warning(f"[DB] update_step: {e}")
        return False
