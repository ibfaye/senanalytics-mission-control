"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowsApi } from "@/lib/api/endpoints";
import type { Workflow, WorkflowWithGraph, WorkflowNode, WorkflowEdge, Execution } from "@/lib/types";

export function useWorkflows() {
  return useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowsApi.list(),
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: ["workflows", id],
    queryFn: () => workflowsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string; tags?: string[] }) =>
      workflowsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });
}

export function useSaveWorkflowGraph() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      nodes,
      edges,
    }: {
      id: string;
      nodes: WorkflowNode[];
      edges: WorkflowEdge[];
    }) => workflowsApi.saveGraph(id, nodes, edges),
    onSuccess: (_, { id }) =>
      qc.invalidateQueries({ queryKey: ["workflows", id] }),
  });
}

export function useExecuteWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => workflowsApi.execute(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["executions"] }),
  });
}

export function usePauseWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => workflowsApi.pause(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["executions"] }),
  });
}
