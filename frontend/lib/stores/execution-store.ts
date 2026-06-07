import { create } from "zustand";
import type { Execution, ExecutionStep } from "@/lib/types";

interface ExecutionStore {
  executions: Execution[];
  currentExecution: Execution | null;
  steps: ExecutionStep[];
  setExecutions: (e: Execution[]) => void;
  setCurrentExecution: (e: Execution | null) => void;
  setSteps: (s: ExecutionStep[]) => void;
  updateStep: (stepId: string, updates: Partial<ExecutionStep>) => void;
}

export const useExecutionStore = create<ExecutionStore>((set) => ({
  executions: [],
  currentExecution: null,
  steps: [],
  setExecutions: (executions) => set({ executions }),
  setCurrentExecution: (currentExecution) => set({ currentExecution }),
  setSteps: (steps) => set({ steps }),
  updateStep: (stepId, updates) =>
    set((state) => ({
      steps: state.steps.map((s) =>
        s.id === stepId ? { ...s, ...updates } : s
      ),
    })),
}));
