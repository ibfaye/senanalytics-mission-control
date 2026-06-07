// ─── Workflow Types ──────────────────────────────────────────

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
  nodeType: NodeType;
  label: string;
  positionX: number;
  positionY: number;
  width?: number;
  height?: number;
  config: Record<string, unknown>;
  status: NodeStatus;
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

export type NodeType = "agent" | "tool" | "workflow" | "approval" | "policy" | "condition" | "trigger";
export type NodeStatus = "idle" | "running" | "success" | "failed" | "paused";

// ─── React Flow Node Data (what's stored in React Flow node.data) ──

export interface MeshNodeData {
  label: string;
  status: NodeStatus;
  nodeType: NodeType;
  metrics?: NodeMetrics;
  config?: Record<string, unknown>;
  description?: string;
  [key: string]: unknown;
}

export interface NodeMetrics {
  executionTimeMs: number;
  tokenUsage: number;
  costCents: number;
  confidence: number;
}

// ─── Agent Types ─────────────────────────────────────────────

export interface Agent {
  id: string;
  name: string;
  displayName: string;
  agentType: AgentType;
  description: string;
  systemPrompt?: string;
  modelProvider?: string;
  modelName?: string;
  config: Record<string, unknown>;
  isActive: boolean;
  tools: AgentTool[];
}

export type AgentType = "supervisor" | "discovery" | "classification" | "security" | "compliance" | "risk" | "reporting";

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

// ─── Execution Types ─────────────────────────────────────────

export interface Execution {
  id: string;
  workflowId: string;
  status: ExecutionStatus;
  triggeredBy: string;
  triggerType: "manual" | "scheduled" | "webhook" | "event";
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
  totalTokens: number;
  totalCostCents: number;
  errorMessage?: string;
  steps: ExecutionStep[];
}

export type ExecutionStatus = "pending" | "running" | "completed" | "failed" | "paused" | "cancelled";

export interface ExecutionStep {
  id: string;
  executionId: string;
  nodeId: string;
  agentId?: string;
  stepOrder: number;
  stepType: StepType;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  startedAt?: string;
  completedAt?: string;
  executionTimeMs?: number;
  tokenUsage?: number;
  costCents?: number;
  confidenceScore?: number;
  errorMessage?: string;
}

export type StepType = "agent_call" | "tool_call" | "approval" | "condition" | "sub_workflow" | "transform";

// ─── Approval Types ──────────────────────────────────────────

export interface Approval {
  id: string;
  executionId: string;
  stepId: string;
  nodeId: string;
  status: "pending" | "approved" | "rejected" | "changes_requested";
  requestedBy: string;
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
  changesRequested?: Record<string, unknown>;
  createdAt: string;
}

// ─── Audit Types ─────────────────────────────────────────────

export interface AuditLog {
  id: string;
  action: string;
  actionType: string;
  actor: string;
  details: Record<string, unknown>;
  createdAt: string;
}

// ─── WebSocket Event Types ───────────────────────────────────

export interface WSExecutionUpdate {
  event: string;
  data: {
    executionId: string;
    nodeId: string;
    nodeType?: string;
    nodeLabel?: string;
    status?: NodeStatus;
    progress?: number;
    message?: string;
    output?: Record<string, unknown>;
    metrics?: NodeMetrics;
    error?: string;
    approvalId?: string;
    reason?: string;
    context?: Record<string, unknown>;
    timestamp: string;
  };
}
