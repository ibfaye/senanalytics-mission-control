"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { User, Mail, Shield, Building2, Loader2 } from "lucide-react";

export default function ProfilePage() {
  const { data: current, isLoading } = useQuery({
    queryKey: ["org-current"],
    queryFn: () =>
      api.get<{
        organization: { id: string; name: string; slug: string; plan: string };
        user: { user_id: string; user_name: string; user_email: string; role: string };
      }>("/organizations/current"),
  });

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <h3 className="text-sm font-semibold text-mission-200">Profile</h3>

      {isLoading ? (
        <Loader2 className="h-5 w-5 animate-spin text-mission-500" />
      ) : current ? (
        <>
          {/* User Info */}
          <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-mission-700">
                <User className="h-8 w-8 text-mission-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-mission-100">{current.user.user_name}</h2>
                <div className="flex items-center gap-3 mt-1">
                  <span className="flex items-center gap-1 text-xs text-mission-400">
                    <Mail className="h-3 w-3" />
                    {current.user.user_email}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded bg-mission-800/30 p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="h-3.5 w-3.5 text-agent-amber" />
                  <span className="text-[10px] text-mission-500">Role</span>
                </div>
                <p className="text-sm font-medium text-mission-200">{current.user.role.toUpperCase()}</p>
              </div>
              <div className="rounded bg-mission-800/30 p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Building2 className="h-3.5 w-3.5 text-agent-cyan" />
                  <span className="text-[10px] text-mission-500">Organization</span>
                </div>
                <p className="text-sm font-medium text-mission-200">{current.organization.name}</p>
              </div>
            </div>
          </div>

          {/* Plan */}
          <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-mission-400">Current Plan</p>
                <p className="text-sm font-semibold text-mission-200 mt-0.5">
                  {current.organization.plan.toUpperCase()}
                </p>
              </div>
              <span className="text-[10px] text-mission-600">
                Tenant: {current.organization.slug}
              </span>
            </div>
          </div>

          {/* API Context */}
          <div className="rounded-lg border border-mission-800 bg-mission-900/30 p-4">
            <h4 className="text-xs font-semibold text-mission-400 mb-2">API Context</h4>
            <div className="space-y-1 text-[10px] font-mono text-mission-500">
              <p>X-User-Id: {current.user.user_id}</p>
              <p>X-Org-Id: {current.organization.id}</p>
              <p>X-User-Role: {current.user.role}</p>
            </div>
            <p className="text-[9px] text-mission-600 mt-2">
              These headers are automatically sent with API requests for multi-tenant scoping.
            </p>
          </div>
        </>
      ) : (
        <p className="text-sm text-mission-500">Unable to load profile</p>
      )}
    </div>
  );
}
