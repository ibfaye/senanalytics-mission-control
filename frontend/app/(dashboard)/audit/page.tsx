"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  FileSearch,
  Clock,
  User,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  Pause,
  ShieldCheck,
} from "lucide-react";

interface AuditEntry {
  id: string;
  execution_id: string | null;
  workflow_id: string | null;
  action: string;
  action_type: string;
  actor_email: string;
  details: Record<string, unknown>;
  created_at: string;
}

function ActionIcon({ action_type }: { action_type: string }) {
  const cls = "h-4 w-4 shrink-0";
  switch (action_type) {
    case "workflow_executed":
      return <Play className={`${cls} text-emerald-400`} />;
    case "node_completed":
      return <CheckCircle2 className={`${cls} text-emerald-400`} />;
    case "node_failed":
      return <XCircle className={`${cls} text-red-400`} />;
    case "approval_granted":
      return <ShieldCheck className={`${cls} text-agent-rose`} />;
    case "approval_rejected":
      return <XCircle className={`${cls} text-agent-rose`} />;
    case "approval_requested":
      return <AlertTriangle className={`${cls} text-amber-400`} />;
    case "node_started":
      return <Play className={`${cls} text-agent-cyan`} />;
    case "workflow_deleted":
      return <XCircle className={`${cls} text-red-400`} />;
    default:
      return <FileSearch className={`${cls} text-mission-500`} />;
  }
}

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function AuditPage() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => api.get<AuditEntry[]>("/audit?limit=100"),
    refetchInterval: 30_000,
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">Audit Trail</h3>
        <span className="text-[10px] text-mission-500 font-mono">
          Immutable append-only log · Auto-refresh 30s
        </span>
      </div>

      <div className="rounded-lg border border-mission-800 bg-mission-900/50 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-sm text-mission-500">
            Loading audit trail...
          </div>
        ) : !logs || logs.length === 0 ? (
          <div className="p-8 text-center text-sm text-mission-500">
            No audit entries yet. Execute a workflow to generate audit logs.
          </div>
        ) : (
          <div className="divide-y divide-mission-800">
            {logs.map((entry) => (
              <div
                key={entry.id}
                className="flex items-start gap-3 p-3 hover:bg-mission-800/30 transition-colors"
              >
                <ActionIcon action_type={entry.action_type} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-xs font-medium text-mission-200 font-mono">
                      {entry.action}
                    </p>
                    <span className="rounded-full px-1.5 py-0.5 text-[9px] font-medium bg-mission-800 text-mission-400">
                      {entry.action_type}
                    </span>
                  </div>
                  {entry.details && Object.keys(entry.details).length > 0 && (
                    <p className="text-xs text-mission-400 mt-0.5 truncate">
                      {Object.entries(entry.details)
                        .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
                        .join(" · ")}
                    </p>
                  )}
                  {entry.execution_id && (
                    <p className="text-[10px] text-mission-600 font-mono mt-0.5">
                      exec: {entry.execution_id.slice(0, 8)}...
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-3 text-[10px] text-mission-500 shrink-0">
                  <span className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {entry.actor_email}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatRelativeTime(entry.created_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
