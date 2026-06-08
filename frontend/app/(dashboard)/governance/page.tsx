"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { Shield, Database, GitBranch, User, Lock, AlertTriangle } from "lucide-react";

export default function GovernancePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-governance"],
    queryFn: () =>
      api.get<{
        domains: { count: number; items: { name: string; sensitivity: string; owner: string }[] };
        data_products: number;
        tables: number;
        classifications: { total_columns: number; pii_columns: number; encrypted_pii: number; unencrypted_pii: number };
        lineage_example: { column: string; upstream_count: number; downstream_count: number };
        ownership: { stewards: number };
      }>("/dashboards/governance"),
    refetchInterval: 30_000,
  });

  return (
    <div className="p-6 space-y-6">
      <h3 className="text-sm font-semibold text-mission-200">Governance Dashboard</h3>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Data Domains", value: data?.domains?.count ?? 0, icon: Database, color: "text-agent-violet" },
          { label: "Data Products", value: data?.data_products ?? 0, icon: Shield, color: "text-agent-cyan" },
          { label: "Tables", value: data?.tables ?? 0, icon: GitBranch, color: "text-agent-emerald" },
          { label: "Data Stewards", value: data?.ownership?.stewards ?? 0, icon: User, color: "text-agent-amber" },
        ].map((stat) => (
          <div key={stat.label} className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
            <div className="flex items-center gap-2">
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
              <span className="text-xs text-mission-400">{stat.label}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-mission-100">
              {isLoading ? "…" : stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Classifications */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">Column Classifications</h4>
          {data?.classifications ? (
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-mission-400">Total Columns</span>
                <span className="font-mono text-mission-200">{data.classifications.total_columns}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-amber-400">PII Columns</span>
                <span className="font-mono text-amber-300">{data.classifications.pii_columns}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-emerald-400">Encrypted PII</span>
                <span className="font-mono text-emerald-300">{data.classifications.encrypted_pii}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-red-400">Unencrypted PII</span>
                <span className="font-mono text-red-300">{data.classifications.unencrypted_pii}</span>
              </div>
              {/* Progress bar */}
              <div className="h-2 rounded-full bg-mission-800 overflow-hidden mt-2">
                <div className="h-full bg-red-500 rounded-full"
                  style={{ width: `${data.classifications.total_columns ? (data.classifications.unencrypted_pii / data.classifications.total_columns) * 100 : 0}%` }} />
              </div>
            </div>
          ) : (
            <p className="text-xs text-mission-500">Loading…</p>
          )}
        </div>

        {/* Domains */}
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">Data Domains</h4>
          {data?.domains?.items ? (
            <div className="space-y-2">
              {data.domains.items.map((domain) => (
                <div key={domain.name} className="flex items-center justify-between rounded bg-mission-800/50 px-3 py-2">
                  <span className="text-xs text-mission-200">{domain.name}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    domain.sensitivity === "HIGH" ? "bg-red-950 text-red-400" : "bg-mission-800 text-mission-400"
                  }`}>
                    {domain.sensitivity}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-mission-500">Loading…</p>
          )}
        </div>
      </div>

      {/* Lineage */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
        <h4 className="text-xs font-semibold text-mission-400 mb-2">
          Lineage: <span className="text-agent-emerald font-mono">{data?.lineage_example?.column ?? "email"}</span>
        </h4>
        <p className="text-xs text-mission-500">
          {data?.lineage_example
            ? `${data.lineage_example.upstream_count} upstream · ${data.lineage_example.downstream_count} downstream mappings`
            : "Loading…"}
        </p>
      </div>
    </div>
  );
}
