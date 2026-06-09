"use client";

import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
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
  ChevronDown,
  Loader2,
} from "lucide-react";

const nodeTemplates = [
  { type: "agent" as const, label: "Agent", icon: Bot, color: "text-agent-emerald", hasPicker: true },
  { type: "tool" as const, label: "Tool", icon: Wrench, color: "text-agent-amber" },
  { type: "workflow" as const, label: "Sub-Workflow", icon: Workflow, color: "text-agent-cyan" },
  { type: "approval" as const, label: "Approval", icon: ShieldCheck, color: "text-agent-rose" },
  { type: "policy" as const, label: "Policy", icon: ScrollText, color: "text-agent-violet" },
  { type: "condition" as const, label: "Condition", icon: GitBranch, color: "text-agent-orange" },
  { type: "trigger" as const, label: "Trigger", icon: Zap, color: "text-mission-300" },
];

interface AgentSummary {
  id: string;
  name: string;
  displayName: string;
  agentType: string;
  isActive: boolean;
}

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
  const [pickerOpen, setPickerOpen] = useState(false);

  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: () => api.get<AgentSummary[]>("/agents"),
    staleTime: 30_000,
  });

  const handleAddNode = useCallback(
    (type: string, agentConfig?: { agentType?: string; agentId?: string; displayName?: string }) => {
      const now = Date.now();
      addNode({
        id: `node-${now}`,
        workflowId,
        nodeType: type,
        label: agentConfig?.displayName
          ? `${agentConfig.displayName}`
          : `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
        positionX: 100 + Math.random() * 400,
        positionY: 100 + Math.random() * 300,
        config: agentConfig || {},
        status: "idle",
      });
    },
    [workflowId, addNode]
  );

  return (
    <div className="flex items-center gap-2 rounded-lg border border-mission-800 bg-mission-900/80 p-2 backdrop-blur relative">
      {nodeTemplates.map((tpl) => (
        <div key={tpl.type} className="relative">
          {tpl.hasPicker ? (
            <>
              <button
                onClick={() => setPickerOpen(!pickerOpen)}
                className="flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs font-medium
                  text-mission-300 hover:bg-mission-800 hover:text-mission-100 transition-colors"
              >
                <tpl.icon className={`h-3.5 w-3.5 ${tpl.color}`} />
                {tpl.label}
                <ChevronDown className="h-3 w-3" />
              </button>
              {pickerOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setPickerOpen(false)}
                  />
                  <div className="absolute top-full left-0 mt-1 z-20 w-64 rounded-lg border border-mission-700 bg-mission-900 shadow-xl">
                    <div className="p-1.5 border-b border-mission-800">
                      <span className="text-[10px] text-mission-500 font-medium">
                        Select Agent Type
                      </span>
                    </div>
                    <div className="max-h-56 overflow-y-auto p-1">
                      {!agents ? (
                        <div className="flex items-center justify-center py-4">
                          <Loader2 className="h-4 w-4 text-mission-500 animate-spin" />
                        </div>
                      ) : (
                        agents.filter(a => a.isActive).map((agent) => (
                          <button
                            key={agent.id}
                            onClick={() => {
                              handleAddNode("agent", {
                                agentType: agent.agentType,
                                agentId: agent.id,
                                displayName: agent.displayName,
                              });
                              setPickerOpen(false);
                            }}
                            className="flex items-center gap-2 w-full rounded-md px-2.5 py-2 text-xs
                              text-mission-300 hover:bg-mission-800 hover:text-mission-100 transition-colors text-left"
                          >
                            <Bot className="h-3.5 w-3.5 text-agent-emerald shrink-0" />
                            <div className="min-w-0">
                              <p className="font-medium truncate">{agent.displayName}</p>
                              <p className="text-[10px] text-mission-500">{agent.agentType}</p>
                            </div>
                          </button>
                        ))
                      )}
                    </div>
                    <div className="border-t border-mission-800 p-1.5">
                      <button
                        onClick={() => {
                          handleAddNode("agent", {
                            agentType: "agent",
                            description: "Generic agent node",
                          });
                          setPickerOpen(false);
                        }}
                        className="flex items-center gap-2 w-full rounded-md px-2.5 py-2 text-xs
                          text-mission-400 hover:bg-mission-800 hover:text-mission-200 transition-colors"
                      >
                        <Bot className="h-3.5 w-3.5 text-mission-500" />
                        Generic Agent (no type)
                      </button>
                    </div>
                  </div>
                </>
              )}
            </>
          ) : (
            <button
              onClick={() => handleAddNode(tpl.type)}
              className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium
                text-mission-300 hover:bg-mission-800 hover:text-mission-100 transition-colors"
              title={`Add ${tpl.label} node`}
            >
              <tpl.icon className={`h-3.5 w-3.5 ${tpl.color}`} />
              {tpl.label}
            </button>
          )}
        </div>
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
