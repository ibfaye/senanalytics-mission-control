"use client";

import { usePathname } from "next/navigation";
import { Bell, Settings, User } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/mission-control": "Mission Control",
  "/governance": "Governance Dashboard",
  "/security": "Security Dashboard",
  "/compliance": "Compliance Dashboard",
  "/workflows": "Workflows",
  "/agents": "Agent Registry",
  "/audit": "Audit Trail",
};

export function Header() {
  const pathname = usePathname();

  // Match base path
  const title = Object.entries(pageTitles).find(([key]) =>
    pathname.startsWith(key)
  )?.[1] || "Mission Control";

  return (
    <header className="flex h-14 items-center justify-between border-b border-mission-800 bg-mission-900 px-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2">
        <div className="flex h-2 w-2 rounded-full bg-agent-emerald animate-pulse" />
        <h2 className="text-sm font-semibold text-mission-200">{title}</h2>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button className="rounded-md p-1.5 text-mission-400 hover:bg-mission-800 hover:text-mission-200 transition-colors">
          <Bell className="h-4 w-4" />
        </button>
        <button className="rounded-md p-1.5 text-mission-400 hover:bg-mission-800 hover:text-mission-200 transition-colors">
          <Settings className="h-4 w-4" />
        </button>
        <button className="flex items-center gap-2 rounded-md p-1.5 text-mission-400 hover:bg-mission-800 hover:text-mission-200 transition-colors">
          <User className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
