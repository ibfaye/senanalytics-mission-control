// ─── API Endpoints ───────────────────────────────────────────
import { api } from "./client";
import type {
  Workflow,
  WorkflowWithGraph,
  WorkflowNode,
  WorkflowEdge,
  Agent,
  Execution,
  Approval,
  AuditLog,
} from "@/lib/types";

// Workflows
export const workflowsApi = {
  list: () => api.get<Workflow[]>("/workflows"),
  get: (id: string) => api.get<WorkflowWithGraph>(`/workflows/${id}`),
  create: (data: { name: string; description?: string; tags?: string[] }) =>
    api.post<Workflow>("/workflows", data),
  update: (id: string, data: Partial<Workflow>) =>
    api.put<Workflow>(`/workflows/${id}`, data),
  delete: (id: string) => api.delete(`/workflows/${id}`),
  execute: (id: string, input?: Record<string, unknown>) =>
    api.post<Execution>(`/workflows/${id}/execute`, { input }),
  pause: (id: string) => api.post<Execution>(`/workflows/${id}/pause`),
  resume: (id: string) => api.post<Execution>(`/workflows/${id}/resume`),
  saveGraph: (id: string, nodes: WorkflowNode[], edges: WorkflowEdge[]) =>
    api.put(`/workflows/${id}/nodes`, { nodes, edges }),
};

// Agents
export const agentsApi = {
  list: () => api.get<Agent[]>("/agents"),
  get: (id: string) => api.get<Agent>(`/agents/${id}`),
};

// Executions
export const executionsApi = {
  list: (workflowId?: string) =>
    api.get<Execution[]>(`/executions${workflowId ? `?workflowId=${workflowId}` : ""}`),
  get: (id: string) => api.get<Execution>(`/executions/${id}`),
};

// Approvals
export const approvalsApi = {
  pending: () => api.get<Approval[]>("/approvals?status=pending"),
  approve: (id: string, reason?: string) =>
    api.post<Approval>(`/approvals/${id}/approve`, { reason }),
  reject: (id: string, reason: string) =>
    api.post<Approval>(`/approvals/${id}/reject`, { reason }),
};

// Audit
export const auditApi = {
  query: (params?: Record<string, string>) =>
    api.get<AuditLog[]>(`/audit?${new URLSearchParams(params).toString()}`),
};
