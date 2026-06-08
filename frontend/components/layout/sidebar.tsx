"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Shield,
  Lock,
  ScrollText,
  Workflow,
  Bot,
  FileSearch,
  Plug,
  Network,
  FileText,
  Building2,
  User,
} from "lucide-react";

const navItems = [
  {
    label: "Mission Control",
    href: "/mission-control",
    icon: LayoutDashboard,
    color: "text-agent-cyan",
  },
  {
    label: "Governance",
    href: "/governance",
    icon: Shield,
    color: "text-agent-violet",
  },
  {
    label: "Security",
    href: "/security",
    icon: Lock,
    color: "text-agent-rose",
  },
  {
    label: "Compliance",
    href: "/compliance",
    icon: ScrollText,
    color: "text-agent-emerald",
  },
  {
    label: "Workflows",
    href: "/workflows",
    icon: Workflow,
    color: "text-agent-amber",
  },
  {
    label: "Agents",
    href: "/agents",
    icon: Bot,
    color: "text-agent-emerald",
  },
  {
    label: "MCP Servers",
    href: "/mcp",
    icon: Plug,
    color: "text-agent-amber",
  },
  {
    label: "Knowledge Graph",
    href: "/knowledge",
    icon: Network,
    color: "text-agent-violet",
  },
  {
    label: "Reports",
    href: "/reports",
    icon: FileText,
    color: "text-agent-cyan",
  },
  {
    label: "Audit Trail",
    href: "/audit",
    icon: FileSearch,
    color: "text-mission-400",
  },
  {
    label: "Organization",
    href: "/organization",
    icon: Building2,
    color: "text-agent-amber",
  },
  {
    label: "Profile",
    href: "/profile",
    icon: User,
    color: "text-mission-400",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-56 flex-col border-r border-mission-800 bg-mission-900">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2 border-b border-mission-800 px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-agent-cyan/20">
          <LayoutDashboard className="h-4 w-4 text-agent-cyan" />
        </div>
        <div>
          <p className="text-xs font-bold text-mission-100">Sen'Analytics</p>
          <p className="text-[10px] text-mission-500">Mission Control</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto p-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-mission-800 text-mission-100"
                  : "text-mission-400 hover:bg-mission-800/50 hover:text-mission-200"
              )}
            >
              <item.icon className={cn("h-4 w-4", isActive ? item.color : "")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-mission-800 p-3">
        <Link href="/profile" className="flex items-center gap-2 text-xs text-mission-500 hover:text-mission-300 transition-colors">
          <div className="h-6 w-6 rounded-full bg-mission-700" />
          <span>ibfaye</span>
        </Link>
      </div>
    </aside>
  );
}
