"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  Bot,
  Plus,
  Pencil,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Loader2,
  X,
  Check,
} from "lucide-react";

interface Agent {
  id: string;
  name: string;
  displayName: string;
  agentType: string;
  description: string;
  systemPrompt: string | null;
  modelProvider: string | null;
  modelName: string | null;
  isActive: boolean;
  tools: string[];
  createdAt: string;
  updatedAt: string;
}

interface AgentForm {
  name: string;
  displayName: string;
  agentType: string;
  description: string;
  systemPrompt: string;
  modelProvider: string;
  modelName: string;
}

const EMPTY_FORM: AgentForm = {
  name: "", displayName: "", agentType: "agent",
  description: "", systemPrompt: "", modelProvider: "", modelName: "",
};

const AGENT_TYPE_LABELS: Record<string, string> = {
  supervisor: "Supervisor",
  discovery: "Discovery",
  classification: "Classification",
  security: "Security",
  compliance: "Compliance",
  risk: "Risk",
  reporting: "Reporting",
  agent: "Custom Agent",
};

export default function AgentsPage() {
  const qc = useQueryClient();
  const [editing, setEditing] = useState<Agent | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<AgentForm>(EMPTY_FORM);

  const { data: agents, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => api.get<Agent[]>("/agents"),
  });

  const createMutation = useMutation({
    mutationFn: (data: AgentForm) => api.post<Agent>("/agents", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["agents"] });
      setCreating(false);
      setForm(EMPTY_FORM);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: { id: string } & Partial<AgentForm & { isActive: boolean }>) =>
      api.put(`/agents/${id}`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["agents"] });
      setEditing(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/agents/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["agents"] }),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      api.put(`/agents/${id}`, { isActive }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["agents"] }),
  });

  const startEdit = (agent: Agent) => {
    setEditing(agent);
    setForm({
      name: agent.name,
      displayName: agent.displayName,
      agentType: agent.agentType,
      description: agent.description,
      systemPrompt: agent.systemPrompt || "",
      modelProvider: agent.modelProvider || "",
      modelName: agent.modelName || "",
    });
  };

  const handleSave = () => {
    if (editing) {
      updateMutation.mutate({ id: editing.id, ...form });
    }
  };

  const handleCreate = () => {
    if (!form.name || !form.displayName) return;
    createMutation.mutate(form);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">Agent Registry</h3>
        <button
          onClick={() => { setCreating(true); setForm(EMPTY_FORM); }}
          className="flex items-center gap-1.5 rounded-md bg-agent-emerald px-3 py-1.5 text-xs font-semibold text-emerald-950 hover:bg-emerald-400 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          New Agent
        </button>
      </div>

      {/* Create / Edit Form */}
      {(creating || editing) && (
        <div className="rounded-lg border border-agent-emerald/30 bg-mission-900 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-agent-emerald">
              {editing ? `Editing: ${editing.displayName}` : "Create Agent"}
            </span>
            <button
              onClick={() => { setCreating(false); setEditing(null); }}
              className="text-mission-500 hover:text-mission-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-mission-500 block mb-1">Name (slug)</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="my-custom-agent"
                className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
              />
            </div>
            <div>
              <label className="text-[10px] text-mission-500 block mb-1">Display Name</label>
              <input
                value={form.displayName}
                onChange={(e) => setForm({ ...form, displayName: e.target.value })}
                placeholder="My Custom Agent"
                className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-[10px] text-mission-500 block mb-1">Type</label>
              <select
                value={form.agentType}
                onChange={(e) => setForm({ ...form, agentType: e.target.value })}
                className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 focus:border-agent-cyan focus:outline-none"
              >
                {Object.entries(AGENT_TYPE_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-mission-500 block mb-1">Model Provider</label>
              <input
                value={form.modelProvider}
                onChange={(e) => setForm({ ...form, modelProvider: e.target.value })}
                placeholder="openai"
                className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
              />
            </div>
            <div>
              <label className="text-[10px] text-mission-500 block mb-1">Model Name</label>
              <input
                value={form.modelName}
                onChange={(e) => setForm({ ...form, modelName: e.target.value })}
                placeholder="gpt-4o-mini"
                className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-[10px] text-mission-500 block mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs text-mission-200 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[10px] text-mission-500 block mb-1">System Prompt</label>
            <textarea
              value={form.systemPrompt}
              onChange={(e) => setForm({ ...form, systemPrompt: e.target.value })}
              rows={3}
              className="w-full rounded-md border border-mission-700 bg-mission-950 px-2.5 py-1.5 text-xs font-mono text-mission-300 placeholder-mission-600 focus:border-agent-cyan focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => { setCreating(false); setEditing(null); }}
              className="rounded-md px-3 py-1.5 text-xs text-mission-400 hover:text-mission-200"
            >
              Cancel
            </button>
            <button
              onClick={editing ? handleSave : handleCreate}
              disabled={updateMutation.isPending || createMutation.isPending}
              className="flex items-center gap-1.5 rounded-md bg-agent-cyan px-3 py-1.5 text-xs font-semibold text-cyan-950 hover:bg-cyan-400 transition-colors disabled:opacity-50"
            >
              {(updateMutation.isPending || createMutation.isPending) ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Check className="h-3.5 w-3.5" />
              )}
              {editing ? "Save Changes" : "Create Agent"}
            </button>
          </div>
        </div>
      )}

      {/* Agent List */}
      {isLoading ? (
        <div className="text-center text-sm text-mission-500 py-8">Loading agents...</div>
      ) : (
        <div className="grid gap-3">
          {agents?.map((agent) => (
            <div
              key={agent.id}
              className={`flex items-center justify-between rounded-lg border p-4 transition-colors ${
                agent.isActive
                  ? "border-mission-800 bg-mission-900/50"
                  : "border-mission-800/50 bg-mission-900/30 opacity-60"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-md ${
                  agent.isActive ? "bg-emerald-950" : "bg-mission-800"
                }`}>
                  <Bot className={`h-4 w-4 ${agent.isActive ? "text-agent-emerald" : "text-mission-500"}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-mission-200">
                    {agent.displayName}
                  </p>
                  <p className="text-xs text-mission-500">
                    {agent.description || agent.agentType}
                  </p>
                  {agent.modelName && (
                    <p className="text-[10px] text-mission-600 font-mono mt-0.5">
                      {agent.modelProvider}/{agent.modelName}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-mission-600 font-mono">{agent.agentType}</span>

                <button
                  onClick={() => toggleMutation.mutate({ id: agent.id, isActive: !agent.isActive })}
                  className="text-mission-500 hover:text-mission-300 transition-colors"
                  title={agent.isActive ? "Deactivate" : "Activate"}
                >
                  {agent.isActive ? (
                    <ToggleRight className="h-4 w-4 text-agent-emerald" />
                  ) : (
                    <ToggleLeft className="h-4 w-4" />
                  )}
                </button>

                <button
                  onClick={() => startEdit(agent)}
                  className="rounded p-1 text-mission-500 hover:bg-mission-800 hover:text-mission-200 transition-colors"
                >
                  <Pencil className="h-3.5 w-3.5" />
                </button>

                <button
                  onClick={() => { if (confirm(`Delete ${agent.displayName}?`)) deleteMutation.mutate(agent.id); }}
                  className="rounded p-1 text-mission-500 hover:bg-red-950 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
