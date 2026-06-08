"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { ScrollText } from "lucide-react";

const frameworkColors: Record<string, { bg: string; text: string; bar: string }> = {
  COMPLIANT: { bg: "bg-emerald-950", text: "text-emerald-400", bar: "bg-emerald-500" },
  PARTIALLY_COMPLIANT: { bg: "bg-amber-950", text: "text-amber-400", bar: "bg-amber-500" },
  NON_COMPLIANT: { bg: "bg-red-950", text: "text-red-400", bar: "bg-red-500" },
};

export default function CompliancePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-compliance"],
    queryFn: () =>
      api.get<{
        frameworks: Record<string, {
          status: string; score: number; gaps: number;
          policies_mapped: number; controls_implemented: number; last_audit: string;
        }>;
        total_policies: number;
        total_controls: number;
        compliance_gaps_count: number;
      }>("/dashboards/compliance"),
    refetchInterval: 30_000,
  });

  return (
    <div className="p-6 space-y-6">
      <h3 className="text-sm font-semibold text-mission-200">Compliance Dashboard</h3>

      {/* Framework Cards */}
      <div className="grid grid-cols-5 gap-3">
        {data?.frameworks && Object.entries(data.frameworks).map(([name, fw]) => {
          const colors = frameworkColors[fw.status] || frameworkColors.PARTIALLY_COMPLIANT;
          return (
            <div key={name} className={`rounded-lg border p-4 text-center ${
              fw.status === "COMPLIANT" ? "border-emerald-800 bg-emerald-950/20" :
              fw.status === "NON_COMPLIANT" ? "border-red-800 bg-red-950/20" :
              "border-amber-800 bg-amber-950/20"
            }`}>
              <p className="text-xs text-mission-400 mb-1">{name}</p>
              <p className={`text-2xl font-bold ${colors.text}`}>{fw.score}%</p>
              <div className="h-1.5 rounded-full bg-mission-800 mt-2 overflow-hidden">
                <div className={`h-full rounded-full ${colors.bar}`}
                  style={{ width: `${fw.score}%` }} />
              </div>
              <div className="flex justify-between mt-2 text-[9px] text-mission-500">
                <span>{fw.gaps} gaps</span>
                <span>{fw.controls_implemented} controls</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Policies Mapped", value: data?.total_policies ?? 0 },
          { label: "Controls Defined", value: data?.total_controls ?? 0 },
          { label: "Compliance Gaps", value: data?.compliance_gaps_count ?? 0 },
        ].map((stat) => (
          <div key={stat.label} className="rounded-lg border border-mission-800 bg-mission-900/50 p-4 text-center">
            <p className="text-xs text-mission-400">{stat.label}</p>
            <p className="mt-1 text-xl font-bold text-mission-100">{isLoading ? "…" : stat.value}</p>
          </div>
        ))}
      </div>

      {/* Framework Detail Table */}
      {data?.frameworks && (
        <div className="rounded-lg border border-mission-800 bg-mission-900/50 overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-mission-800 text-mission-400">
                <th className="text-left p-3">Framework</th>
                <th className="text-center p-3">Score</th>
                <th className="text-center p-3">Status</th>
                <th className="text-center p-3">Gaps</th>
                <th className="text-center p-3">Policies</th>
                <th className="text-center p-3">Controls</th>
                <th className="text-center p-3">Last Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-mission-800">
              {Object.entries(data.frameworks).map(([name, fw]) => (
                <tr key={name} className="hover:bg-mission-800/30">
                  <td className="p-3 font-medium text-mission-200">{name}</td>
                  <td className="p-3 text-center font-mono">{fw.score}%</td>
                  <td className="p-3 text-center">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                      frameworkColors[fw.status]?.bg || ""} ${frameworkColors[fw.status]?.text || ""}`}>
                      {fw.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="p-3 text-center text-red-400">{fw.gaps}</td>
                  <td className="p-3 text-center">{fw.policies_mapped}</td>
                  <td className="p-3 text-center text-emerald-400">{fw.controls_implemented}</td>
                  <td className="p-3 text-center text-mission-500">{fw.last_audit}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
