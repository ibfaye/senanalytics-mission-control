"use client";

import { useToast } from "@/components/ui/use-toast";
import { X } from "lucide-react";

export function Toaster() {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="flex items-center gap-3 rounded-lg border border-mission-800 bg-mission-900 px-4 py-3 text-sm text-mission-200 shadow-lg animate-in slide-in-from-right"
        >
          <span>{toast.title || toast.description}</span>
          <button onClick={() => dismiss(toast.id)} className="text-mission-500 hover:text-mission-300">
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
}
