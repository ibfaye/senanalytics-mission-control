"use client";

import { ShieldCheck, X, CheckCircle2, AlertTriangle } from "lucide-react";

interface ApprovalData {
  executionId: string;
  approvalId: string;
  nodeId: string;
  nodeLabel: string;
  reason: string;
  context?: Record<string, unknown>;
}

interface ApprovalDialogProps {
  data: ApprovalData;
  onApprove: (approvalId: string) => void;
  onReject: (approvalId: string) => void;
}

export function ApprovalDialog({
  data,
  onApprove,
  onReject,
}: ApprovalDialogProps) {
  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-mission-950/80 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-xl border-2 border-agent-rose/40 bg-mission-900 shadow-2xl shadow-agent-rose/10">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-mission-800 px-6 py-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-rose-950/60">
            <ShieldCheck className="h-5 w-5 text-agent-rose" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-mission-100">
              Human Approval Required
            </h3>
            <p className="text-xs text-mission-400">{data.nodeLabel}</p>
          </div>
        </div>

        {/* Body */}
        <div className="space-y-4 px-6 py-4">
          <div className="rounded-lg border border-mission-800 bg-mission-950/50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <span className="text-xs font-medium text-mission-300">
                Review Request
              </span>
            </div>
            <p className="text-sm text-mission-200 leading-relaxed">
              {data.reason}
            </p>
          </div>

          <div className="rounded-lg border border-mission-800 bg-mission-950/50 p-3">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-mission-500">Node ID</span>
                <p className="font-mono text-mission-300">{data.nodeId}</p>
              </div>
              <div>
                <span className="text-mission-500">Execution</span>
                <p className="font-mono text-mission-300 truncate">
                  {data.executionId.slice(0, 8)}...
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 border-t border-mission-800 px-6 py-4">
          <button
            onClick={() => onReject(data.approvalId)}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-red-800 bg-red-950/40 px-4 py-2.5 text-sm font-medium text-red-400 hover:bg-red-950/70 hover:text-red-300 transition-colors"
          >
            <X className="h-4 w-4" />
            Reject
          </button>
          <button
            onClick={() => onApprove(data.approvalId)}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-agent-emerald px-4 py-2.5 text-sm font-semibold text-emerald-950 hover:bg-emerald-400 transition-colors"
          >
            <CheckCircle2 className="h-4 w-4" />
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
