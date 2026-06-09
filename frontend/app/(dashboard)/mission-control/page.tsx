"use client";

import { useWorkflows, useExecuteWorkflow } from "@/lib/hooks/use-workflows";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  Activity,
  Bot,
  ShieldCheck,
  AlertTriangle,
  Play,
  Pause,
  RotateCw,
  X,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import Link from "next/link";

interface ExecutionSummary {
  id: string;
  workflow_id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  total_tokens: number;
  total_cost_cents: number;
  error_message: string | null;
  output: Record<string, unknown> | null;
  steps: { status: string }[];
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    running: "bg-emerald-950 text-emerald-400 border-emerald-800",
    completed: "bg-emerald-950/60 text-emerald-500 border-emerald-800/50",
    failed: "bg-red-950 text-red-400 border-red-800",
    cancelled: "bg-mission-800 text-mission-400 border-mission-700",
    paused: "bg-amber-950 text-amber-400 border-amber-800",
    pending: "bg-mission-800 text-mission-500 border-mission-700",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium ${
        styles[status] || styles.pending
      }`}
    >
      {status === "running" && <Loader2 className="h-3 w-3 animate-spin" />}
      {status === "completed" && <CheckCircle2 className="h-3 w-3" />}
      {status === "failed" && <XCircle className="h-3 w-3" />}
      {status === "paused" && <Pause className="h-3 w-3" />}
      {status}
    </span>
  );
}

function formatDuration(ms: number | null): string {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function formatRelative(iso: string | null): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return `${secs}s ago`;
  return `${Math.floor(secs / 60)}m ago`;
}

export default function MissionControlPage() {
  const { data: workflows, isLoading: wfLoading } = useWorkflows();
  const executeMutation = useExecuteWorkflow();
  const qc = useQueryClient();

  // Live execution polling
  const { data: executions } = useQuery({
    queryKey: ["executions"],
    queryFn: () => api.get<ExecutionSummary[]>("/executions"),
    refetchInterval: 5_000,
  });

  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: () => api.get<{ isActive: boolean }[]>("/agents"),
    staleTime: 60_000,
  });

  // Execution control mutations
  const pauseMutation = useMutation({
    mutationFn: (id: string) => api.post(`/executions/${id}/pause`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["executions"] }),
  });
  const resumeMutation = useMutation({
    mutationFn: (id: string) => api.post(`/executions/${id}/resume`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["executions"] }),
  });
  const cancelMutation = useMutation({
    mutationFn: (id: string) => api.post(`/executions/${id}/cancel`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["executions"] }),
  });

  const activeWorkflows = workflows?.filter((w) => w.status === "active").length || 0;
  const runningAgents = agents?.filter((a) => a.isActive).length || 0;
  const openApprovals = executions?.filter(
    (e) => e.status === "running" || e.status === "paused"
  ).length || 0;
  const recentExecutions = executions?.length || 0;

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

      {/* Live Executions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-mission-200">
            Live Executions
          </h3>
          <span className="text-[10px] text-mission-500 font-mono">
            Auto-refresh 5s
          </span>
        </div>

        <div className="rounded-lg border border-mission-800 bg-mission-900/50 overflow-hidden">
          {!executions || executions.length === 0 ? (
            <div className="p-8 text-center text-sm text-mission-500">
              No executions yet. Execute a workflow to see live status.
            </div>
          ) : (
            <div className="divide-y divide-mission-800">
              {executions.slice(0, 20).map((exec) => (
                <div
                  key={exec.id}
                  className="flex items-center justify-between p-3 hover:bg-mission-800/30 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <StatusBadge status={exec.status} />
                    <div className="min-w-0">
                      <Link
                        href={`/workflows/${exec.workflow_id}`}
                        className="text-xs font-medium text-mission-200 hover:text-mission-100 font-mono truncate block"
                      >
                        {exec.id.slice(0, 8)}...
                      </Link>
                      <div className="flex items-center gap-3 text-[10px] text-mission-500 mt-0.5">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatRelative(exec.started_at)}
                        </span>
                        <span>{formatDuration(exec.duration_ms)}</span>
                        <span>{exec.total_tokens} tok</span>
                        <span>${((exec.total_cost_cents || 0) / 100).toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Controls */}
                  <div className="flex items-center gap-1 shrink-0">
                    {(exec.status === "running" || exec.status === "paused") && (
                      <>
                        {exec.status === "running" ? (
                          <button
                            onClick={() => pauseMutation.mutate(exec.id)}
                            className="rounded p-1.5 text-mission-400 hover:bg-mission-700 hover:text-amber-400 transition-colors"
                            title="Pause"
                          >
                            <Pause className="h-3.5 w-3.5" />
                          </button>
                        ) : (
                          <button
                            onClick={() => resumeMutation.mutate(exec.id)}
                            className="rounded p-1.5 text-mission-400 hover:bg-mission-700 hover:text-emerald-400 transition-colors"
                            title="Resume"
                          >
                            <Play className="h-3.5 w-3.5" />
                          </button>
                        )}
                        <button
                          onClick={() => cancelMutation.mutate(exec.id)}
                          className="rounded p-1.5 text-mission-400 hover:bg-mission-700 hover:text-red-400 transition-colors"
                          title="Cancel"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </>
                    )}
                    {exec.status === "completed" && (
                      <span className="text-[10px] text-mission-500">
                        {exec.steps?.length || 0} steps
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
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
          {wfLoading ? (
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
                        ${
                          wf.status === "active"
                            ? "bg-emerald-950 text-emerald-400"
                            : "bg-mission-800 text-mission-400"
                        }`}
                    >
                      {wf.status}
                    </span>
                    <button
                      onClick={() => executeMutation.mutate(wf.id)}
                      disabled={executeMutation.isPending}
                      className="flex items-center gap-1.5 rounded-md bg-mission-800 px-2.5 py-1 text-[11px] text-mission-300
                        hover:bg-mission-700 hover:text-mission-100 transition-colors disabled:opacity-50"
                    >
                      {executeMutation.isPending ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Play className="h-3 w-3" />
                      )}
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
