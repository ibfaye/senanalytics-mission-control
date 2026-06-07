import { create } from "zustand";

interface UIStore {
  sidebarOpen: boolean;
  activeDashboard: string;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveDashboard: (d: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  activeDashboard: "mission-control",
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setActiveDashboard: (d) => set({ activeDashboard: d }),
}));
