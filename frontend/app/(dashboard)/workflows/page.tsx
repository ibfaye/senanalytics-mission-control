"use client";

import { useWorkflows, useCreateWorkflow } from "@/lib/hooks/use-workflows";
import Link from "next/link";
import { Workflow, Plus, Play } from "lucide-react";

export default function WorkflowsPage() {
  const { data: workflows, isLoading } = useWorkflows();
  const createMutation = useCreateWorkflow();

  const handleCreate = () => {
    createMutation.mutate(
      { name: `Workflow ${(workflows?.length || 0) + 1}`, description: "New governance workflow" },
      {
        onSuccess: (data) => {
          window.location.href = `/workflows/${data.id}`;
        },
      }
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">
          Workflows
        </h3>
        <button
          onClick={handleCreate}
          className="flex items-center gap-1.5 rounded-md bg-agent-cyan px-3 py-1.5 text-xs font-semibold text-cyan-950 hover:bg-cyan-400 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          New Workflow
        </button>
      </div>

      <div className="grid gap-4">
        {isLoading ? (
          <p className="text-sm text-mission-500">Loading...</p>
        ) : workflows && workflows.length > 0 ? (
          workflows.map((wf) => (
            <Link
              key={wf.id}
              href={`/workflows/${wf.id}`}
              className="flex items-center justify-between rounded-lg border border-mission-800 bg-mission-900/50 p-4 hover:border-mission-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-mission-800">
                  <Workflow className="h-4 w-4 text-mission-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-mission-200">
                    {wf.name}
                  </p>
                  <p className="text-xs text-mission-500">
                    {wf.description} · v{wf.version}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium
                    ${wf.status === "active"
                      ? "bg-emerald-950 text-emerald-400"
                      : "bg-mission-800 text-mission-400"
                    }`}
                >
                  {wf.status}
                </span>
              </div>
            </Link>
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-mission-700 p-12 text-center">
            <Workflow className="mx-auto h-8 w-8 text-mission-600 mb-3" />
            <p className="text-sm text-mission-500">No workflows yet</p>
            <button
              onClick={handleCreate}
              className="mt-3 text-xs text-agent-cyan hover:underline"
            >
              Create your first workflow
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
