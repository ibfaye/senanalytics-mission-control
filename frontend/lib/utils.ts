// ─── Utilities ─────────────────────────────────────────────────
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

export function formatTokens(n: number): string {
  if (n < 1000) return `${n}`;
  if (n < 1000000) return `${(n / 1000).toFixed(1)}K`;
  return `${(n / 1000000).toFixed(1)}M`;
}

export function formatCost(cents: number): string {
  if (cents === 0) return "$0.00";
  return `$${(cents / 100).toFixed(2)}`;
}

export const STATUS_COLORS = {
  idle: { border: "border-mission-600", bg: "bg-mission-800", text: "text-mission-400" },
  running: { border: "border-agent-emerald", bg: "bg-emerald-950", text: "text-agent-emerald" },
  success: { border: "border-emerald-500", bg: "bg-emerald-950", text: "text-emerald-400" },
  failed: { border: "border-red-500", bg: "bg-red-950", text: "text-red-400" },
  paused: { border: "border-amber-500", bg: "bg-amber-950", text: "text-amber-400" },
} as const;
