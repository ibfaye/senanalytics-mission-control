import { Shield, Database, GitBranch } from "lucide-react";

export default function GovernancePage() {
  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Data Domains", value: 8, icon: Database, color: "text-agent-violet" },
          { label: "Data Products", value: 24, icon: Shield, color: "text-agent-cyan" },
          { label: "Lineage Mappings", value: 156, icon: GitBranch, color: "text-agent-emerald" },
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
        <Shield className="mx-auto h-8 w-8 text-mission-600 mb-3" />
        <p className="text-sm text-mission-500">Governance dashboard will display data domains, classifications, and lineage.</p>
        <p className="text-xs text-mission-600 mt-1">Phase 5 — Neo4j Knowledge Graph integration</p>
      </div>
    </div>
  );
}
