# Event Model & API Contracts — Sen'Analytics Mission Control

---

## Event Model

### Core Domain Events

Every action in the system produces a typed domain event. Events flow through Redis Streams
and are consumed by the WebSocket server, audit logger, and notification system.

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW LIFECYCLE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Draft ──► Active ──► Executing ──► Completed                │
│                                             │                │
│                                             ├── Failed       │
│                                             └── Paused       │
│                                                  │           │
│                                                  └── Resumed  │
└─────────────────────────────────────────────────────────────┘
```

### Event Types

```typescript
// Workflow events
interface WorkflowCreatedEvent {
  type: "workflow.created";
  workflowId: string;
  name: string;
  createdBy: string;
  timestamp: string;
}

interface WorkflowUpdatedEvent {
  type: "workflow.updated";
  workflowId: string;
  changes: Record<string, unknown>;
  updatedBy: string;
  timestamp: string;
}

interface WorkflowExecutionStartedEvent {
  type: "workflow.execution.started";
  executionId: string;
  workflowId: string;
  workflowName: string;
  triggeredBy: string;
  triggerType: "manual" | "scheduled" | "webhook" | "event";
  input?: Record<string, unknown>;
  timestamp: string;
}

interface WorkflowExecutionCompletedEvent {
  type: "workflow.execution.completed";
  executionId: string;
  workflowId: string;
  durationMs: number;
  totalTokens: number;
  totalCostCents: number;
  stepsCompleted: number;
  timestamp: string;
}

interface WorkflowExecutionFailedEvent {
  type: "workflow.execution.failed";
  executionId: string;
  workflowId: string;
  error: string;
  failedStepId: string;
  timestamp: string;
}

// Node execution events (streamed live via WebSocket)
interface NodeStartedEvent {
  type: "node.started";
  executionId: string;
  nodeId: string;
  nodeType: string;
  nodeLabel: string;
  timestamp: string;
}

interface NodeProgressEvent {
  type: "node.progress";
  executionId: string;
  nodeId: string;
  progress: number;       // 0-100
  message: string;
  timestamp: string;
}

interface NodeCompletedEvent {
  type: "node.completed";
  executionId: string;
  nodeId: string;
  output: Record<string, unknown>;
  metrics: NodeMetrics;
  timestamp: string;
}

interface NodeFailedEvent {
  type: "node.failed";
  executionId: string;
  nodeId: string;
  error: string;
  retryable: boolean;
  timestamp: string;
}

// Approval events
interface ApprovalRequestedEvent {
  type: "approval.requested";
  executionId: string;
  approvalId: string;
  nodeId: string;
  nodeLabel: string;
  requestedBy: string;
  reason: string;
  context: Record<string, unknown>;
  expiresAt: string;
  timestamp: string;
}

interface ApprovalRespondedEvent {
  type: "approval.responded";
  executionId: string;
  approvalId: string;
  decision: "approved" | "rejected" | "changes_requested";
  approvedBy: string;
  reason?: string;
  timestamp: string;
}

// Agent events
interface AgentDecisionEvent {
  type: "agent.decision";
  executionId: string;
  agentId: string;
  agentType: string;
  stepId: string;
  decision: string;
  rationale: string;
  confidence: number;
  timestamp: string;
}

// Metrics
interface NodeMetrics {
  executionTimeMs: number;
  tokenUsage: number;
  costCents: number;
  confidence: number;
}

// Audit event
interface AuditEvent {
  type: "audit.logged";
  action: string;
  actionType: string;
  actor: string;
  details: Record<string, unknown>;
  timestamp: string;
}
```

---

## WebSocket Protocol

### Connection

```
ws://localhost:8000/ws/workflows/{workflowId}?token={jwt}
```

### Server → Client Messages

```json
{
  "event": "node.started",
  "data": {
    "executionId": "uuid",
    "nodeId": "uuid",
    "nodeType": "security",
    "nodeLabel": "Security Scan",
    "timestamp": "2026-06-07T12:00:00Z"
  }
}
```

```json
{
  "event": "node.progress",
  "data": {
    "executionId": "uuid",
    "nodeId": "uuid",
    "progress": 45,
    "message": "Scanning IAM policies...",
    "timestamp": "2026-06-07T12:00:05Z"
  }
}
```

```json
{
  "event": "node.completed",
  "data": {
    "executionId": "uuid",
    "nodeId": "uuid",
    "output": { "findings": 3, "critical": 1 },
    "metrics": {
      "executionTimeMs": 1250,
      "tokenUsage": 850,
      "costCents": 2,
      "confidence": 0.92
    },
    "timestamp": "2026-06-07T12:00:08Z"
  }
}
```

```json
{
  "event": "approval.requested",
  "data": {
    "executionId": "uuid",
    "approvalId": "uuid",
    "nodeId": "uuid",
    "nodeLabel": "Apply Remediation",
    "requestedBy": "ConsensusArbitrator",
    "reason": "PII encryption remediation requires human authorization",
    "context": {
      "remediationPlan": "Enable TDE on customer-db-prod-01",
      "impactedData": "1500000 customer records",
      "riskScore": 0.63
    },
    "expiresAt": "2026-06-07T13:00:00Z",
    "timestamp": "2026-06-07T12:00:10Z"
  }
}
```

```json
{
  "event": "workflow.execution.completed",
  "data": {
    "executionId": "uuid",
    "workflowId": "uuid",
    "durationMs": 8500,
    "totalTokens": 3200,
    "totalCostCents": 12,
    "stepsCompleted": 5,
    "timestamp": "2026-06-07T12:00:15Z"
  }
}
```

### Client → Server Message

```json
{
  "action": "approval.respond",
  "data": {
    "approvalId": "uuid",
    "decision": "approved",
    "reason": "Verified PII encryption is required and remediation plan is safe"
  }
}
```

---

## REST API Contracts

### Base URL: `http://localhost:8000/api`

### Authentication

All endpoints require `Authorization: Bearer <jwt_token>` header.

### Workflows

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/workflows` | List workflows | Query: `?status=active&limit=20&offset=0` | `Workflow[]` |
| POST | `/workflows` | Create workflow | `{ name, description?, tags? }` | `Workflow` |
| GET | `/workflows/:id` | Get workflow with nodes/edges | - | `WorkflowWithGraph` |
| PUT | `/workflows/:id` | Update workflow | `{ name?, description?, status? }` | `Workflow` |
| DELETE | `/workflows/:id` | Soft-delete workflow | - | `{ deleted: true }` |
| POST | `/workflows/:id/execute` | Execute workflow | `{ input? }` | `Execution` |
| POST | `/workflows/:id/pause` | Pause execution | - | `Execution` |
| POST | `/workflows/:id/resume` | Resume execution | - | `Execution` |
| POST | `/workflows/:id/cancel` | Cancel execution | - | `Execution` |
| GET | `/workflows/:id/nodes` | Get workflow nodes | - | `WorkflowNode[]` |
| PUT | `/workflows/:id/nodes` | Save workflow nodes/edges | `{ nodes, edges }` | `{ saved: true }` |

### Agents

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/agents` | List agents | Query: `?type=security&active=true` | `Agent[]` |
| POST | `/agents` | Register agent | `{ name, displayName, agentType, ... }` | `Agent` |
| GET | `/agents/:id` | Get agent details | - | `Agent` |
| PUT | `/agents/:id` | Update agent | `{ displayName?, config?, ... }` | `Agent` |
| DELETE | `/agents/:id` | Deactivate agent | - | `{ deactivated: true }` |
| GET | `/agents/:id/tools` | List agent tools | - | `AgentTool[]` |
| POST | `/agents/:id/tools` | Register tool | `{ toolName, toolSchema, ... }` | `AgentTool` |
| DELETE | `/agents/:id/tools/:toolId` | Remove tool | - | `{ removed: true }` |

### Executions

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/executions` | List executions | Query: `?workflowId=&status=&limit=20` | `Execution[]` |
| GET | `/executions/:id` | Get execution details | - | `Execution` |
| GET | `/executions/:id/steps` | Get execution steps | - | `ExecutionStep[]` |
| GET | `/executions/:id/approvals` | Get execution approvals | - | `Approval[]` |

### Approvals

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/approvals` | List pending approvals | Query: `?status=pending` | `Approval[]` |
| POST | `/approvals/:id/approve` | Approve | `{ reason? }` | `Approval` |
| POST | `/approvals/:id/reject` | Reject | `{ reason }` | `Approval` |
| POST | `/approvals/:id/request-changes` | Request changes | `{ changes }` | `Approval` |

### Audit

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/audit` | Query audit logs | Query: `?executionId=&actionType=&actor=&from=&to=&limit=50` | `AuditLog[]` |
| GET | `/audit/:id` | Get single audit entry | - | `AuditLog` |
| GET | `/audit/export` | Export audit trail | Query: `?format=csv|json&from=&to=` | File |

### Knowledge Graph

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/knowledge/nodes` | Query nodes | Query: `?type=DataDomain` | `KnowledgeNode[]` |
| GET | `/knowledge/nodes/:id` | Get node with relationships | - | `KnowledgeNode` |
| GET | `/knowledge/lineage` | Trace lineage | Query: `?columnName=email` | `LineageResult` |
| GET | `/knowledge/impact` | Impact analysis | Query: `?policyId=` | `ImpactResult` |

### MCP Servers

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| GET | `/mcp/servers` | List MCP servers | - | `MCPServer[]` |
| POST | `/mcp/servers` | Register MCP server | `{ name, adapterType, connectionConfig }` | `MCPServer` |
| POST | `/mcp/servers/:id/test` | Test connection | - | `{ success, message }` |
| GET | `/mcp/servers/:id/tools` | Discover tools | - | `MCPTool[]` |

### Dashboards

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/dashboards/mission-control` | Active workflows, agents, costs | `MissionControlMetrics` |
| GET | `/dashboards/governance` | Domains, classifications, lineage | `GovernanceMetrics` |
| GET | `/dashboards/security` | Findings, vulnerabilities, posture | `SecurityMetrics` |
| GET | `/dashboards/compliance` | Framework status, gaps | `ComplianceMetrics` |

---

## TypeScript Types (Frontend)

```typescript
// lib/types/workflow.ts
export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: "draft" | "active" | "archived";
  version: number;
  createdBy: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowWithGraph extends Workflow {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowNode {
  id: string;
  workflowId: string;
  nodeType: "agent" | "tool" | "workflow" | "approval" | "policy" | "condition" | "trigger";
  label: string;
  positionX: number;
  positionY: number;
  width?: number;
  height?: number;
  config: Record<string, unknown>;
  status: "idle" | "running" | "success" | "failed" | "paused";
}

export interface WorkflowEdge {
  id: string;
  workflowId: string;
  sourceNodeId: string;
  targetNodeId: string;
  sourceHandle?: string;
  targetHandle?: string;
  edgeType: "default" | "smoothstep" | "straight" | "step";
  label?: string;
  condition?: Record<string, unknown>;
  animated: boolean;
}

// lib/types/agent.ts
export interface Agent {
  id: string;
  name: string;
  displayName: string;
  agentType: "supervisor" | "discovery" | "classification" | "security" | "compliance" | "risk" | "reporting";
  description: string;
  systemPrompt?: string;
  modelProvider?: string;
  modelName?: string;
  config: Record<string, unknown>;
  isActive: boolean;
  tools: AgentTool[];
}

export interface AgentTool {
  id: string;
  agentId: string;
  toolName: string;
  displayName?: string;
  description?: string;
  toolSchema: Record<string, unknown>;
  mcpServer?: string;
  isActive: boolean;
}
```

---

## Pydantic Models (Backend)

```python
# backend/app/schemas/workflow.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class NodeType(str, Enum):
    AGENT = "agent"
    TOOL = "tool"
    WORKFLOW = "workflow"
    APPROVAL = "approval"
    POLICY = "policy"
    CONDITION = "condition"
    TRIGGER = "trigger"

class NodeStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] = []

class WorkflowNodeCreate(BaseModel):
    node_type: NodeType
    label: str
    position_x: float = 0
    position_y: float = 0
    width: float | None = None
    height: float | None = None
    config: dict = {}

class WorkflowEdgeCreate(BaseModel):
    source_node_id: UUID
    target_node_id: UUID
    source_handle: str | None = None
    target_handle: str | None = None
    edge_type: str = "default"
    label: str | None = None
    condition: dict | None = None

class SaveGraphRequest(BaseModel):
    nodes: list[WorkflowNodeCreate]
    edges: list[WorkflowEdgeCreate]

class ExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    total_tokens: int
    total_cost_cents: int
    error_message: str | None
```

---

## WebSocket Event Flow Diagram

```
User clicks "Execute" on workflow canvas
        │
        ▼
Frontend: POST /api/workflows/:id/execute
        │
        ▼
FastAPI: Create Execution record → status: "pending"
FastAPI: Push to Redis Stream "executions"
        │
        ▼
LangGraph Runner: Pick up execution from Redis Stream
LangGraph: Set execution status → "running"
LangGraph: Publish "workflow.execution.started" → Redis
        │
        ▼
Redis → WebSocket Server → Frontend
Frontend: React Flow canvas shows workflow as "running"
        │
        ▼
LangGraph: Process node 1 (Discovery Agent)
LangGraph: Publish "node.started" → Redis → WS → Frontend
Frontend: Node 1 border pulses green (running)
        │
        ▼
LangGraph: Agent completes, returns result
LangGraph: Publish "node.completed" with metrics → Redis → WS → Frontend
Frontend: Node 1 border turns solid green (success)
        │
        ▼
... (continue for all nodes) ...
        │
        ▼
LangGraph: Hit approval node
LangGraph: Publish "approval.requested" → Redis → WS → Frontend
Frontend: Show approval dialog
        │
        ▼
User clicks "Approve"
Frontend: POST /api/approvals/:id/approve
Frontend: Send WS message `{ action: "approval.respond", ... }`
        │
        ▼
LangGraph: Resume from checkpoint
LangGraph: Continue processing remaining nodes
        │
        ▼
LangGraph: All nodes complete
LangGraph: Publish "workflow.execution.completed" → Redis → WS → Frontend
Frontend: Success toast + final metrics display
```
