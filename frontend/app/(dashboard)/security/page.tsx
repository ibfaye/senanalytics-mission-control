import { Lock, AlertTriangle, ShieldCheck } from "lucide-react";

export default function SecurityPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Open Findings", value: 12, icon: AlertTriangle, color: "text-agent-rose" },
          { label: "Critical Risks", value: 3, icon: Lock, color: "text-red-400" },
          { label: "Passed Controls", value: 45, icon: ShieldCheck, color: "text-agent-emerald" },
        ].map((stat) => (
          <div key={stat.label} className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
            <div className="flex items-center gap-2">
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
              <span className="text-xs text-mission-400">{stat.label}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-mission-100">{stat.value}</p>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-12 text-center">
        <Lock className="mx-auto h-8 w-8 text-mission-600 mb-3" />
        <p className="text-sm text-mission-500">Security dashboard will show findings, vulnerabilities, and risk scores.</p>
        <p className="text-xs text-mission-600 mt-1">Phase 6 — Security Agent integration</p>
      </div>
    </div>
  );
}
