"use client";

import { useWorkflows, useExecuteWorkflow } from "@/lib/hooks/use-workflows";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  Activity,
  Bot,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";

export default function MissionControlPage() {
  const { data: workflows, isLoading } = useWorkflows();
  const executeMutation = useExecuteWorkflow();

  // Live stats from the API
  const { data: executions } = useQuery({
    queryKey: ["executions"],
    queryFn: () => api.get<{ status: string }[]>("/executions"),
    refetchInterval: 10_000,
  });
  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: () => api.get<{ isActive: boolean }[]>("/agents"),
    staleTime: 60_000,
  });

  const activeWorkflows = workflows?.filter((w) => w.status === "active").length || 0;
  const runningAgents = agents?.filter((a) => a.isActive).length || 0;
  const recentExecutions = executions?.length || 0;
  const openApprovals = executions?.filter((e) => e.status === "running" || e.status === "paused").length || 0;

  const stats = [
    { label: "Active Workflows", value: activeWorkflows, icon: Activity, color: "text-agent-cyan" },
    { label: "Running Agents", value: runningAgents, icon: Bot, color: "text-agent-emerald" },
    { label: "Pending Approvals", value: openApprovals, icon: AlertTriangle, color: "text-agent-rose" },
    { label: "Recent Executions", value: recentExecutions, icon: ShieldCheck, color: "text-agent-amber" },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Stats grid */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg border border-mission-800 bg-mission-900/50 p-4"
          >
            <div className="flex items-center gap-2">
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
              <span className="text-xs text-mission-400">{stat.label}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-mission-100">
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Recent Workflows */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-mission-200">
            Recent Workflows
          </h3>
          <Link
            href="/workflows/new"
            className="rounded-md bg-agent-cyan px-3 py-1.5 text-xs font-semibold text-cyan-950 hover:bg-cyan-400 transition-colors"
          >
            + New Workflow
          </Link>
        </div>

        <div className="rounded-lg border border-mission-800 bg-mission-900/50">
          {isLoading ? (
            <div className="p-8 text-center text-sm text-mission-500">
              Loading workflows...
            </div>
          ) : workflows && workflows.length > 0 ? (
            <div className="divide-y divide-mission-800">
              {workflows.map((wf) => (
                <div
                  key={wf.id}
                  className="flex items-center justify-between p-4 hover:bg-mission-800/30 transition-colors"
                >
                  <div>
                    <Link
                      href={`/workflows/${wf.id}`}
                      className="text-sm font-medium text-mission-200 hover:text-mission-100"
                    >
                      {wf.name}
                    </Link>
                    <p className="text-xs text-mission-500 mt-0.5">
                      {wf.description || "No description"} · v{wf.version}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium
                        ${wf.status === "active"
                          ? "bg-emerald-950 text-emerald-400"
                          : "bg-mission-800 text-mission-400"
                        }`}
                    >
                      {wf.status}
                    </span>
                    <button
                      onClick={() => executeMutation.mutate(wf.id)}
                      className="rounded-md bg-mission-800 px-2.5 py-1 text-[11px] text-mission-300
                        hover:bg-mission-700 hover:text-mission-100 transition-colors"
                    >
                      Execute
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-sm text-mission-500">No workflows yet</p>
              <Link
                href="/workflows/new"
                className="mt-2 inline-block text-xs text-agent-cyan hover:underline"
              >
                Create your first workflow
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
