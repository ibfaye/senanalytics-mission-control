"""Pydantic schemas for executions, steps, approvals, and WebSocket events."""

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class StepType(str, Enum):
    AGENT_CALL = "agent_call"
    TOOL_CALL = "tool_call"
    APPROVAL = "approval"
    CONDITION = "condition"
    SUB_WORKFLOW = "sub_workflow"
    TRANSFORM = "transform"


# ─── Execution ─────────────────────────────────────────────

class ExecutionCreate(BaseModel):
    workflow_id: str
    input: Optional[dict] = None
    triggered_by: Optional[str] = "system"


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: ExecutionStatus
    triggered_by: str
    trigger_type: str = "manual"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    total_tokens: int = 0
    total_cost_cents: int = 0
    error_message: Optional[str] = None


class NodeMetrics(BaseModel):
    execution_time_ms: int = 0
    token_usage: int = 0
    cost_cents: int = 0
    confidence: float = 0.0


class ExecutionStepResponse(BaseModel):
    id: str
    execution_id: str
    node_id: str
    agent_id: Optional[str] = None
    step_order: int = 0
    step_type: StepType
    status: StepStatus = StepStatus.PENDING
    input: Optional[dict] = None
    output: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    token_usage: Optional[int] = None
    cost_cents: Optional[int] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None


# ─── Approvals ─────────────────────────────────────────────

class ApprovalRequest(BaseModel):
    approval_id: str = Field(default_factory=lambda: str(uuid4()))
    execution_id: str
    node_id: str
    node_label: str
    requested_by: str
    reason: str
    context: dict = {}
    expires_at: Optional[datetime] = None


class ApprovalResponse(BaseModel):
    approval_id: str
    decision: str  # "approved" | "rejected" | "changes_requested"
    reason: Optional[str] = None
    approved_by: Optional[str] = None


# ─── WebSocket Events ──────────────────────────────────────

class WSEventType(str, Enum):
    NODE_STARTED = "node.started"
    NODE_PROGRESS = "node.progress"
    NODE_COMPLETED = "node.completed"
    NODE_FAILED = "node.failed"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_RESPONDED = "approval.responded"
    WORKFLOW_STARTED = "workflow.execution.started"
    WORKFLOW_COMPLETED = "workflow.execution.completed"
    WORKFLOW_FAILED = "workflow.execution.failed"
    METRICS_UPDATE = "metrics.update"


class WSMessage(BaseModel):
    event: str
    data: dict


class WSNodeStarted(BaseModel):
    execution_id: str
    node_id: str
    node_type: str = ""
    node_label: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WSNodeCompleted(BaseModel):
    execution_id: str
    node_id: str
    output: Optional[dict] = None
    metrics: NodeMetrics = Field(default_factory=NodeMetrics)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WSNodeFailed(BaseModel):
    execution_id: str
    node_id: str
    error: str
    retryable: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WSApprovalRequested(BaseModel):
    execution_id: str
    approval_id: str
    node_id: str
    node_label: str
    requested_by: str
    reason: str
    context: dict = {}
    expires_at: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Agent Types ───────────────────────────────────────────

class AgentType(str, Enum):
    SUPERVISOR = "supervisor"
    DISCOVERY = "discovery"
    CLASSIFICATION = "classification"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    RISK = "risk"
    REPORTING = "reporting"


class AgentConfig(BaseModel):
    name: str
    display_name: str
    agent_type: AgentType
    description: str = ""
    system_prompt: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
