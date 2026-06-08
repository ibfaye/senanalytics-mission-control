"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  Network,
  GitBranch,
  AlertTriangle,
  Search,
  Database,
  Shield,
  ScrollText,
  User,
  FileText,
  Loader2,
} from "lucide-react";

const labelIcons: Record<string, typeof Network> = {
  DataDomain: Database,
  DataProduct: Network,
  Table: Database,
  Column: Search,
  Policy: ScrollText,
  Control: Shield,
  Owner: User,
  Risk: AlertTriangle,
  Incident: AlertTriangle,
  Report: FileText,
};

const labelColors: Record<string, string> = {
  DataDomain: "text-cyan-400",
  DataProduct: "text-blue-400",
  Table: "text-violet-400",
  Column: "text-emerald-400",
  Policy: "text-amber-400",
  Control: "text-rose-400",
  Risk: "text-red-400",
  Incident: "text-red-500",
  Owner: "text-gray-400",
  Report: "text-green-400",
};

export default function KnowledgePage() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ["kg-summary"],
    queryFn: () => api.get<{ total_nodes: number; total_edges: number; labels: Record<string, number> }>("/knowledge/summary"),
  });

  const { data: risks } = useQuery({
    queryKey: ["kg-risks"],
    queryFn: () => api.get<{ id: string; labels: string[]; properties: Record<string, unknown> }[]>("/knowledge/risks"),
  });

  const { data: gaps } = useQuery({
    queryKey: ["kg-gaps"],
    queryFn: () => api.get<{ id: string; labels: string[]; properties: Record<string, unknown> }[]>("/knowledge/compliance/gaps"),
  });

  const { data: lineage, isLoading: loadingLineage } = useQuery({
    queryKey: ["kg-lineage", "email"],
    queryFn: () =>
      api.get<{
        column: { properties: Record<string, unknown> };
        upstream_lineage: { node: { properties: Record<string, unknown>; labels: string[] }; relationship: string }[];
        downstream_mappings: { node: { properties: Record<string, unknown>; labels: string[] }; relationship: string }[];
      }>("/knowledge/lineage?column=email"),
  });

  const labelEntries = summary?.labels ? Object.entries(summary.labels).sort(([, a], [, b]) => b - a) : [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">
          Knowledge Graph Explorer
        </h3>
        <span className="text-[10px] text-mission-500 font-mono">
          Neo4j-powered Governance Graph
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <div className="flex items-center gap-2">
            <Network className="h-4 w-4 text-agent-cyan" />
            <span className="text-xs text-mission-400">Total Nodes</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-mission-100">
            {loadingSummary ? <Loader2 className="h-5 w-5 animate-spin" /> : summary?.total_nodes || 0}
          </p>
        </div>
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-agent-violet" />
            <span className="text-xs text-mission-400">Relationships</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-mission-100">
            {loadingSummary ? <Loader2 className="h-5 w-5 animate-spin" /> : summary?.total_edges || 0}
          </p>
        </div>
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-agent-rose" />
            <span className="text-xs text-mission-400">Open Risks</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-mission-100">
            {risks?.length || 0}
          </p>
        </div>
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-agent-amber" />
            <span className="text-xs text-mission-400">Compliance Gaps</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-mission-100">
            {gaps?.length || 0}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Label Distribution */}
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">
            Node Types
          </h4>
          <div className="space-y-2">
            {labelEntries.map(([label, count]) => {
              const Icon = labelIcons[label] || Network;
              return (
                <div key={label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-3.5 w-3.5 ${labelColors[label] || "text-mission-400"}`} />
                    <span className="text-xs text-mission-300">{label}</span>
                  </div>
                  <span className="text-xs font-mono text-mission-400">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Risk Heatmap */}
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">
            Risk Heatmap
          </h4>
          {risks && risks.length > 0 ? (
            <div className="space-y-2">
              {risks.map((risk) => (
                <div key={risk.id} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-mission-300 truncate max-w-[180px]">
                        {risk.properties.name as string}
                      </span>
                      <span
                        className={`text-[10px] font-medium px-1.5 py-0.5 rounded
                          ${risk.properties.severity === "CRITICAL" ? "bg-red-950 text-red-400" :
                            risk.properties.severity === "HIGH" ? "bg-amber-950 text-amber-400" :
                            "bg-mission-800 text-mission-400"}`}>
                        {risk.properties.severity as string}
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-mission-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-agent-rose transition-all"
                        style={{ width: `${(Number(risk.properties.score) * 100).toFixed(0)}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-0.5">
                      <span className="text-[9px] text-mission-600">
                        L: {risk.properties.likelihood as number}
                      </span>
                      <span className="text-[9px] text-mission-600">
                        I: {risk.properties.impact as number}
                      </span>
                      <span className="text-[9px] font-mono text-mission-500">
                        {(Number(risk.properties.score) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-mission-500">No risks registered</p>
          )}
        </div>
      </div>

      {/* Lineage Example: email column */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
        <h4 className="text-xs font-semibold text-mission-400 mb-3">
          Lineage Trace: <span className="text-agent-emerald font-mono">email</span>
        </h4>
        {loadingLineage ? (
          <Loader2 className="h-4 w-4 animate-spin text-mission-500" />
        ) : lineage && !("error" in lineage) ? (
          <div className="flex items-center gap-2 flex-wrap text-xs">
            {/* Upstream */}
            {lineage.upstream_lineage?.map((item, i) => (
              <span key={i} className="flex items-center gap-1">
                <span className="px-2 py-1 rounded bg-mission-800 text-mission-300">
                  {item.node.properties.name as string}
                </span>
                <span className="text-mission-600">→</span>
              </span>
            ))}
            {/* Column */}
            <span className="px-2 py-1 rounded bg-emerald-950 text-emerald-400 font-mono">
              {lineage.column?.properties.name as string}
            </span>
            {/* Downstream */}
            {lineage.downstream_mappings?.map((item, i) => (
              <span key={i} className="flex items-center gap-1">
                <span className="text-mission-600">→</span>
                <span className={`px-2 py-1 rounded bg-mission-800/50 text-xs ${labelColors[item.node.labels?.[0]] || "text-mission-400"}`}>
                  {item.node.properties.name as string}
                </span>
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-mission-500">No lineage data</p>
        )}
      </div>

      {/* Compliance Gaps */}
      {gaps && gaps.length > 0 && (
        <div className="rounded-lg border border-amber-800 bg-amber-950/20 p-4">
          <h4 className="text-xs font-semibold text-amber-400 mb-3">
            ⚠️ Compliance Gaps — PII columns with no mapped control
          </h4>
          <div className="flex flex-wrap gap-2">
            {gaps.map((gap) => (
              <span
                key={gap.id}
                className="px-2 py-1 rounded bg-amber-950 border border-amber-800 text-xs text-amber-300 font-mono">
                {gap.properties.name as string}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
