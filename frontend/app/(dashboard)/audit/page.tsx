import { FileSearch, Clock, User } from "lucide-react";

const mockAuditLogs = [
  { action: "workflow.executed", actor: "ibfaye", time: "2 min ago", details: "Security Scan executed on prod-db" },
  { action: "agent.completed", actor: "system", time: "5 min ago", details: "Classification Agent completed PII scan" },
  { action: "approval.granted", actor: "ibfaye", time: "15 min ago", details: "Approved encryption remediation plan" },
  { action: "node.started", actor: "system", time: "20 min ago", details: "Discovery Agent started schema analysis" },
  { action: "workflow.created", actor: "ibfaye", time: "1 hour ago", details: "Created 'GDPR Compliance Audit' workflow" },
];

export default function AuditPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">Audit Trail</h3>
        <span className="text-[10px] text-mission-500 font-mono">
          Immutable append-only log
        </span>
      </div>

      <div className="rounded-lg border border-mission-800 bg-mission-900/50 overflow-hidden">
        <div className="divide-y divide-mission-800">
          {mockAuditLogs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 p-3 hover:bg-mission-800/30 transition-colors">
              <FileSearch className="mt-0.5 h-4 w-4 text-mission-500 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-mission-200 font-mono">
                  {log.action}
                </p>
                <p className="text-xs text-mission-400 mt-0.5">{log.details}</p>
              </div>
              <div className="flex items-center gap-3 text-[10px] text-mission-500 shrink-0">
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {log.actor}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {log.time}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
