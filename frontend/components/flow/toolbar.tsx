"use client";

import { useCallback } from "react";
import { useWorkflowStore } from "@/lib/stores/workflow-store";
import {
  Bot,
  Wrench,
  Workflow,
  ShieldCheck,
  ScrollText,
  GitBranch,
  Zap,
  Play,
  Save,
} from "lucide-react";

const nodeTemplates = [
  { type: "agent" as const, label: "Agent", icon: Bot, color: "text-agent-emerald" },
  { type: "tool" as const, label: "Tool", icon: Wrench, color: "text-agent-amber" },
  { type: "workflow" as const, label: "Sub-Workflow", icon: Workflow, color: "text-agent-cyan" },
  { type: "approval" as const, label: "Approval", icon: ShieldCheck, color: "text-agent-rose" },
  { type: "policy" as const, label: "Policy", icon: ScrollText, color: "text-agent-violet" },
  { type: "condition" as const, label: "Condition", icon: GitBranch, color: "text-agent-orange" },
  { type: "trigger" as const, label: "Trigger", icon: Zap, color: "text-mission-300" },
];

interface WorkflowToolbarProps {
  workflowId: string;
  onExecute?: () => void;
  onSave?: () => void;
  isExecuting?: boolean;
}

export function WorkflowToolbar({
  workflowId,
  onExecute,
  onSave,
  isExecuting = false,
}: WorkflowToolbarProps) {
  const addNode = useWorkflowStore((s) => s.addNode);

  const handleAddNode = useCallback(
    (type: (typeof nodeTemplates)[number]["type"]) => {
      const now = Date.now();
      addNode({
        id: `node-${now}`,
        workflowId,
        nodeType: type,
        label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
        positionX: 100 + Math.random() * 400,
        positionY: 100 + Math.random() * 300,
        config: {},
        status: "idle",
      });
    },
    [workflowId, addNode]
  );

  return (
    <div className="flex items-center gap-2 rounded-lg border border-mission-800 bg-mission-900/80 p-2 backdrop-blur">
      {nodeTemplates.map((tpl) => (
        <button
          key={tpl.type}
          onClick={() => handleAddNode(tpl.type)}
          className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium
            text-mission-300 hover:bg-mission-800 hover:text-mission-100 transition-colors"
          title={`Add ${tpl.label} node`}
        >
          <tpl.icon className={`h-3.5 w-3.5 ${tpl.color}`} />
          {tpl.label}
        </button>
      ))}

      <div className="mx-2 h-6 w-px bg-mission-700" />

      <button
        onClick={onSave}
        className="flex items-center gap-1.5 rounded-md bg-mission-800 px-3 py-1.5 text-xs font-medium
          text-mission-200 hover:bg-mission-700 transition-colors"
      >
        <Save className="h-3.5 w-3.5" />
        Save
      </button>

      <button
        onClick={onExecute}
        disabled={isExecuting}
        className="flex items-center gap-1.5 rounded-md bg-agent-emerald px-3 py-1.5 text-xs font-semibold
          text-emerald-950 hover:bg-emerald-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Play className="h-3.5 w-3.5" />
        Execute
      </button>
    </div>
  );
}
