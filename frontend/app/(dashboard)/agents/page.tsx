import { Bot, Wrench, ShieldCheck } from "lucide-react";

const builtInAgents = [
  { name: "Supervisor", type: "supervisor", status: "active", description: "Orchestrates workflows: plans, routes, delegates, aggregates." },
  { name: "Discovery", type: "discovery", status: "active", description: "Discovers and catalogs data sources, analyzes schemas." },
  { name: "Classification", type: "classification", status: "active", description: "Detects PII, PHI, SPI and sensitive data types." },
  { name: "Security", type: "security", status: "active", description: "Reviews security posture, IAM, vulnerabilities." },
  { name: "Compliance", type: "compliance", status: "active", description: "Maps to GDPR, CDP, PIPEDA, SOC2, ISO 27001." },
  { name: "Risk", type: "risk", status: "active", description: "Scores and prioritizes risks, produces heatmaps." },
  { name: "Reporting", type: "reporting", status: "active", description: "Generates executive summaries, audit reports." },
];

export default function AgentsPage() {
  return (
    <div className="p-6 space-y-6">
      <h3 className="text-sm font-semibold text-mission-200">Agent Registry</h3>
      <div className="grid gap-3">
        {builtInAgents.map((agent) => (
          <div
            key={agent.name}
            className="flex items-center justify-between rounded-lg border border-mission-800 bg-mission-900/50 p-4"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-emerald-950">
                <Bot className="h-4 w-4 text-agent-emerald" />
              </div>
              <div>
                <p className="text-sm font-medium text-mission-200">{agent.name} Agent</p>
                <p className="text-xs text-mission-500">{agent.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-emerald-950 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
                {agent.status}
              </span>
              <span className="text-[10px] text-mission-600 font-mono">{agent.type}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
