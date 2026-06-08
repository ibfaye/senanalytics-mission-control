"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { FileText, Download, Loader2, RefreshCw, ExternalLink } from "lucide-react";

const reportTypes = [
  { type: "executive-summary" as const, label: "Executive Summary", desc: "High-level governance overview" },
  { type: "audit" as const, label: "Audit Report", desc: "Detailed findings and evidence" },
  { type: "remediation-plan" as const, label: "Remediation Plan", desc: "Prioritized action items" },
];

export default function ReportsPage() {
  const qc = useQueryClient();

  const { data: reports, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () =>
      api.get<{ id: string; title: string; type: string; generated_at: string }[]>("/reports"),
    refetchInterval: 10_000,
  });

  const generateMutation = useMutation({
    mutationFn: (type: string) => api.post(`/reports/generate/${type}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reports"] }),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">Compliance Reports</h3>
        <span className="text-[10px] text-mission-500 font-mono">
          Auto-generated audit documentation
        </span>
      </div>

      {/* Generate */}
      <div className="grid grid-cols-3 gap-4">
        {reportTypes.map((rt) => (
          <button
            key={rt.type}
            onClick={() => generateMutation.mutate(rt.type)}
            disabled={generateMutation.isPending}
            className="flex flex-col items-center gap-3 rounded-lg border border-mission-800 bg-mission-900/50 p-6
              hover:border-mission-700 hover:bg-mission-900 transition-colors disabled:opacity-50 text-left">
            <FileText className="h-8 w-8 text-agent-cyan" />
            <div className="text-center">
              <p className="text-sm font-medium text-mission-200">{rt.label}</p>
              <p className="text-xs text-mission-500 mt-1">{rt.desc}</p>
            </div>
            {generateMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin text-mission-500" />
            ) : (
              <span className="flex items-center gap-1 text-xs text-agent-cyan">
                <RefreshCw className="h-3 w-3" />
                Generate
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Generated Reports */}
      <div>
        <h4 className="text-xs font-semibold text-mission-400 mb-3">
          Generated Reports ({reports?.length || 0})
        </h4>
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-mission-500" />
        ) : reports && reports.length > 0 ? (
          <div className="space-y-2">
            {reports.map((report) => (
              <div
                key={report.id}
                className="flex items-center justify-between rounded-lg border border-mission-800 bg-mission-900/50 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-agent-cyan" />
                  <div>
                    <p className="text-sm text-mission-200">{report.title}</p>
                    <p className="text-[10px] text-mission-500">
                      {report.type.replace("_", " ")} · {new Date(report.generated_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={`http://localhost:8001/api/reports/${report.id}/download?format=txt`}
                    target="_blank"
                    className="flex items-center gap-1 rounded-md bg-mission-800 px-2.5 py-1 text-[10px] text-mission-300 hover:bg-mission-700 transition-colors">
                    <Download className="h-3 w-3" />
                    TXT
                  </a>
                  <a
                    href={`http://localhost:8001/api/reports/${report.id}/download?format=json`}
                    target="_blank"
                    className="flex items-center gap-1 rounded-md bg-mission-800 px-2.5 py-1 text-[10px] text-mission-300 hover:bg-mission-700 transition-colors">
                    <ExternalLink className="h-3 w-3" />
                    JSON
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-mission-700 p-8 text-center">
            <FileText className="mx-auto h-6 w-6 text-mission-600 mb-2" />
            <p className="text-xs text-mission-500">No reports generated yet</p>
          </div>
        )}
      </div>
    </div>
  );
}
