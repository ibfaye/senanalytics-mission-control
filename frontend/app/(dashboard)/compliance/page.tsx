import { ScrollText, CheckCircle, XCircle } from "lucide-react";

export default function CompliancePage() {
  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "GDPR", status: "85%", color: "text-agent-emerald" },
          { label: "CDP (Senegal)", status: "72%", color: "text-agent-amber" },
          { label: "PIPEDA", status: "90%", color: "text-agent-emerald" },
          { label: "SOC2", status: "68%", color: "text-agent-amber" },
          { label: "ISO 27001", status: "55%", color: "text-agent-rose" },
        ].map((fw) => (
          <div key={fw.label} className="rounded-lg border border-mission-800 bg-mission-900/50 p-4 text-center">
            <p className="text-xs text-mission-400">{fw.label}</p>
            <p className={`mt-2 text-xl font-bold ${fw.color}`}>{fw.status}</p>
            <p className="text-[10px] text-mission-500">compliant</p>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-12 text-center">
        <ScrollText className="mx-auto h-8 w-8 text-mission-600 mb-3" />
        <p className="text-sm text-mission-500">Compliance dashboard will map data assets to regulatory frameworks.</p>
        <p className="text-xs text-mission-600 mt-1">Phase 6 — Compliance Agent integration</p>
      </div>
    </div>
  );
}
