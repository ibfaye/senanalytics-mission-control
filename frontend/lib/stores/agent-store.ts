import { create } from "zustand";
import type { Agent } from "@/lib/types";

interface AgentStore {
  agents: Agent[];
  selectedAgent: Agent | null;
  setAgents: (agents: Agent[]) => void;
  setSelectedAgent: (agent: Agent | null) => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  agents: [],
  selectedAgent: null,
  setAgents: (agents) => set({ agents }),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
}));
