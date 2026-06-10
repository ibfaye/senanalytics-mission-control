import { create } from "zustand";
import type { Workflow, WorkflowNode, WorkflowEdge, NodeStatus } from "@/lib/types";

interface WorkflowStore {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  isExecuting: boolean;
  executionId: string | null;
  _setRfNodes?: unknown; // React Flow setNodes bridge for toolbar

  setWorkflows: (wf: Workflow[]) => void;
  setCurrentWorkflow: (wf: Workflow | null) => void;
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  updateNodeStatus: (nodeId: string, status: NodeStatus) => void;
  setExecuting: (executing: boolean, executionId?: string) => void;
  addNode: (node: WorkflowNode) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (edgeId: string) => void;
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  workflows: [],
  currentWorkflow: null,
  nodes: [],
  edges: [],
  isExecuting: false,
  executionId: null,

  setWorkflows: (workflows) => set({ workflows }),
  setCurrentWorkflow: (currentWorkflow) => set({ currentWorkflow }),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  updateNodeStatus: (nodeId, status) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, status } : n
      ),
    })),

  setExecuting: (isExecuting, executionId) =>
    set({ isExecuting, executionId: executionId ?? null }),

  addNode: (node) =>
    set((state) => ({ nodes: [...state.nodes, node] })),

  removeNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((n) => n.id !== nodeId),
      edges: state.edges.filter(
        (e) => e.sourceNodeId !== nodeId && e.targetNodeId !== nodeId
      ),
    })),

  addEdge: (edge) =>
    set((state) => ({ edges: [...state.edges, edge] })),

  removeEdge: (edgeId) =>
    set((state) => ({
      edges: state.edges.filter((e) => e.id !== edgeId),
    })),
}));
