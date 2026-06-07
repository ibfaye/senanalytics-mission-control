"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { MeshNodeData } from "@/lib/types";
import { STATUS_COLORS } from "@/lib/utils";
import { formatDuration, formatTokens, formatCost } from "@/lib/utils";
import {
  Bot,
  Wrench,
  Workflow,
  ShieldCheck,
  ScrollText,
  GitBranch,
  Zap,
  Loader2,
  CheckCircle2,
  XCircle,
  PauseCircle,
} from "lucide-react";

// ─── Status Icons ──────────────────────────────────────────

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "running":
      return <Loader2 className="h-4 w-4 text-agent-emerald animate-spin" />;
    case "success":
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    case "failed":
      return <XCircle className="h-4 w-4 text-red-400" />;
    case "paused":
      return <PauseCircle className="h-4 w-4 text-amber-400" />;
    default:
      return null;
  }
}

// ─── Node Type Icons ────────────────────────────────────────

function NodeTypeIcon({ nodeType }: { nodeType: string }) {
  switch (nodeType) {
    case "agent":
      return <Bot className="h-3.5 w-3.5 text-agent-emerald" />;
    case "tool":
      return <Wrench className="h-3.5 w-3.5 text-agent-amber" />;
    case "workflow":
      return <Workflow className="h-3.5 w-3.5 text-agent-cyan" />;
    case "approval":
      return <ShieldCheck className="h-3.5 w-3.5 text-agent-rose" />;
    case "policy":
      return <ScrollText className="h-3.5 w-3.5 text-agent-violet" />;
    case "condition":
      return <GitBranch className="h-3.5 w-3.5 text-agent-orange" />;
    case "trigger":
      return <Zap className="h-3.5 w-3.5 text-mission-400" />;
    default:
      return null;
  }
}

// ─── Node Color By Type ─────────────────────────────────────

const NODE_COLORS: Record<string, { border: string; bg: string }> = {
  agent: { border: "border-agent-emerald", bg: "bg-emerald-950/30" },
  tool: { border: "border-agent-amber", bg: "bg-amber-950/30" },
  workflow: { border: "border-agent-cyan", bg: "bg-cyan-950/30" },
  approval: { border: "border-agent-rose", bg: "bg-rose-950/30" },
  policy: { border: "border-agent-violet", bg: "bg-violet-950/30" },
  condition: { border: "border-agent-orange", bg: "bg-orange-950/30" },
  trigger: { border: "border-mission-600", bg: "bg-mission-800/30" },
};

// ─── Agent Node ─────────────────────────────────────────────

export const AgentNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;
  const colors = NODE_COLORS[d.nodeType] || NODE_COLORS.agent;
  const statusColor = STATUS_COLORS[d.status];

  return (
    <div
      className={`relative min-w-[200px] rounded-lg border-2 ${colors.border} ${colors.bg} p-3
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}
        ${d.status === "running" ? "node-running" : ""}
        ${d.status === "failed" ? statusColor.border : ""}
        transition-shadow duration-200`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />

      <div className="flex items-center gap-2">
        <NodeTypeIcon nodeType={d.nodeType} />
        <StatusIcon status={d.status} />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>

      {d.description && (
        <p className="mt-1 text-[11px] text-mission-400 leading-tight">
          {d.description}
        </p>
      )}

      {d.metrics && (
        <div className="mt-2 flex gap-3 text-[10px] text-mission-400 font-mono">
          <span>{formatDuration(d.metrics.executionTimeMs)}</span>
          <span>{formatTokens(d.metrics.tokenUsage)} tok</span>
          <span>{formatCost(d.metrics.costCents)}</span>
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
    </div>
  );
});

AgentNode.displayName = "AgentNode";

// ─── Tool Node ──────────────────────────────────────────────

export const ToolNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;
  const statusColor = STATUS_COLORS[d.status];

  return (
    <div
      className={`relative min-w-[180px] rounded-lg border-2 border-agent-amber bg-amber-950/30 p-3
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}
        ${d.status === "running" ? "node-running" : ""}`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <Wrench className="h-3.5 w-3.5 text-agent-amber" />
        <StatusIcon status={d.status} />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
    </div>
  );
});

ToolNode.displayName = "ToolNode";

// ─── Approval Node ──────────────────────────────────────────

export const ApprovalNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;

  return (
    <div
      className={`relative min-w-[200px] rounded-lg border-2 border-dashed border-agent-rose bg-rose-950/30 p-3
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}
        ${d.status === "running" ? "border-solid node-running" : ""}`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-4 w-4 text-agent-rose" />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>
      <p className="mt-1 text-[10px] text-agent-rose/70 font-mono">
        Human approval required
      </p>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
    </div>
  );
});

ApprovalNode.displayName = "ApprovalNode";

// ─── Policy Node ────────────────────────────────────────────

export const PolicyNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;

  return (
    <div
      className={`relative min-w-[180px] rounded-lg border-2 border-agent-violet bg-violet-950/30 p-3
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <ScrollText className="h-3.5 w-3.5 text-agent-violet" />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
    </div>
  );
});

PolicyNode.displayName = "PolicyNode";

// ─── Condition Node ─────────────────────────────────────────

export const ConditionNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;

  return (
    <div
      className={`relative min-w-[160px] rounded-lg border-2 border-agent-orange bg-orange-950/30 p-3 rotate-1
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}`}
      style={{ transform: "rotate(1deg)" }}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <GitBranch className="h-3.5 w-3.5 text-agent-orange" />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="!bg-emerald-500 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        className="!bg-red-500 !border-2 !border-mission-800 !w-3 !h-3"
      />
    </div>
  );
});

ConditionNode.displayName = "ConditionNode";

// ─── Trigger Node ───────────────────────────────────────────

export const TriggerNode = memo(({ data, selected }: NodeProps) => {
  const d = data as MeshNodeData;

  return (
    <div
      className={`relative min-w-[180px] rounded-full border-2 border-mission-600 bg-mission-800/50 p-3
        ${selected ? "ring-2 ring-agent-cyan ring-offset-2 ring-offset-mission-950" : ""}`}
    >
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-mission-600 !border-2 !border-mission-800 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <Zap className="h-3.5 w-3.5 text-agent-amber" />
        <span className="text-sm font-semibold text-mission-100">
          {d.label}
        </span>
      </div>
    </div>
  );
});

TriggerNode.displayName = "TriggerNode";
