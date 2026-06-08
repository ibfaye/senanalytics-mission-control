"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { Lock, AlertTriangle, ShieldCheck, CheckCircle2, XCircle } from "lucide-react";

export default function SecurityPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-security"],
    queryFn: () =>
      api.get<{
        risk_heatmap: { name: string; score: number; severity: string; likelihood: number; impact: number }[];
        findings: { id: string; category: string; severity: string; description: string; affected: string; remediation: string }[];
        compliance_gaps: { name: string; type: string }[];
        controls: { implemented: number; partial: number; not_implemented: number };
      }>("/dashboards/security"),
    refetchInterval: 30_000,
  });

  return (
    <div className="p-6 space-y-6">
      <h3 className="text-sm font-semibold text-mission-200">Security Dashboard</h3>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Open Findings", value: data?.findings?.length ?? 0, icon: AlertTriangle, color: "text-agent-rose" },
          { label: "Controls Active", value: (data?.controls?.implemented ?? 0) + (data?.controls?.partial ?? 0), icon: ShieldCheck, color: "text-agent-emerald" },
          { label: "Not Implemented", value: data?.controls?.not_implemented ?? 0, icon: XCircle, color: "text-red-400" },
          { label: "Compliance Gaps", value: data?.compliance_gaps?.length ?? 0, icon: Lock, color: "text-agent-amber" },
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

      <div className="grid grid-cols-2 gap-4">
        {/* Findings */}
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">Security Findings</h4>
          {data?.findings ? (
            <div className="space-y-2">
              {data.findings.map((f) => (
                <div key={f.id} className="rounded bg-mission-800/50 px-3 py-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
                      f.severity === "CRITICAL" ? "bg-red-950 text-red-400" :
                      f.severity === "HIGH" ? "bg-amber-950 text-amber-400" :
                      "bg-mission-800 text-mission-400"
                    }`}>{f.severity}</span>
                    <span className="text-[9px] text-mission-600">{f.category}</span>
                  </div>
                  <p className="text-xs text-mission-300">{f.description}</p>
                  <p className="text-[10px] text-mission-500 mt-1">
                    Affected: {f.affected} · Fix: {f.remediation}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-mission-500">Loading…</p>
          )}
        </div>

        {/* Risk Heatmap */}
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
          <h4 className="text-xs font-semibold text-mission-400 mb-3">Risk Heatmap</h4>
          {data?.risk_heatmap ? (
            <div className="space-y-2">
              {data.risk_heatmap.map((risk) => (
                <div key={risk.name} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-mission-300 truncate max-w-[160px]">{risk.name}</span>
                      <span className="text-[10px] font-mono text-mission-400">{(risk.score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-mission-800 overflow-hidden">
                      <div className="h-full bg-agent-rose rounded-full"
                        style={{ width: `${(risk.score * 100).toFixed(0)}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-mission-500">Loading…</p>
          )}
        </div>
      </div>
    </div>
  );
}
