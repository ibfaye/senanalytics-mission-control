"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { Building2, Users, Shield, User, Trash2, Loader2 } from "lucide-react";

const roleColors: Record<string, string> = {
  admin: "bg-agent-rose/20 text-agent-rose",
  editor: "bg-agent-amber/20 text-agent-amber",
  viewer: "bg-mission-800 text-mission-300",
  auditor: "bg-agent-violet/20 text-agent-violet",
};

export default function OrganizationPage() {
  const qc = useQueryClient();

  const { data: current, isLoading: loadingCurrent } = useQuery({
    queryKey: ["org-current"],
    queryFn: () =>
      api.get<{
        organization: { id: string; name: string; slug: string; plan: string };
        user: { user_id: string; user_name: string; user_email: string; role: string };
      }>("/organizations/current"),
  });

  const { data: members, isLoading: loadingMembers } = useQuery({
    queryKey: ["org-members", current?.organization?.id],
    queryFn: () =>
      api.get<
        { user_id: string; user_name: string; user_email: string; role: string; joined_at: string }[]
      >(`/organizations/${current?.organization?.id}/members`),
    enabled: !!current?.organization?.id,
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) =>
      api.delete(`/organizations/${current?.organization?.id}/members/${userId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["org-members"] }),
  });

  return (
    <div className="p-6 space-y-6">
      <h3 className="text-sm font-semibold text-mission-200">Organization</h3>

      {/* Org Card */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-6">
        {loadingCurrent ? (
          <Loader2 className="h-5 w-5 animate-spin text-mission-500" />
        ) : current ? (
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-agent-cyan/20">
                  <Building2 className="h-5 w-5 text-agent-cyan" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-mission-100">{current.organization.name}</h2>
                  <p className="text-xs text-mission-500 font-mono">{current.organization.slug}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 mt-3">
                <span className="flex items-center gap-1.5 text-xs text-mission-400">
                  <Users className="h-3.5 w-3.5" />
                  {members?.length || 0} members
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                  current.organization.plan === "enterprise" ? "bg-agent-violet/20 text-agent-violet" :
                  current.organization.plan === "pro" ? "bg-agent-cyan/20 text-agent-cyan" :
                  "bg-mission-800 text-mission-400"
                }`}>
                  {current.organization.plan.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-mission-400">Your Role</p>
              <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium ${roleColors[current.user.role] || "text-mission-400"}`}>
                {current.user.role.toUpperCase()}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-mission-500">No organization found</p>
        )}
      </div>

      {/* Members */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/50 p-4">
        <h4 className="text-xs font-semibold text-mission-400 mb-3">
          Members ({members?.length || 0})
        </h4>
        {loadingMembers ? (
          <Loader2 className="h-4 w-4 animate-spin text-mission-500" />
        ) : members && members.length > 0 ? (
          <div className="space-y-2">
            {members.map((member) => (
              <div
                key={member.user_id}
                className="flex items-center justify-between rounded bg-mission-800/30 px-3 py-2.5"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-mission-700">
                    <User className="h-3.5 w-3.5 text-mission-400" />
                  </div>
                  <div>
                    <p className="text-xs text-mission-200">{member.user_name}</p>
                    <p className="text-[10px] text-mission-500">{member.user_email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${roleColors[member.role] || "text-mission-400"}`}>
                    {member.role.toUpperCase()}
                  </span>
                  {member.role !== "admin" && (
                    <button
                      onClick={() => removeMemberMutation.mutate(member.user_id)}
                      className="text-mission-600 hover:text-red-400 transition-colors">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-mission-500">No members</p>
        )}
      </div>

      {/* RBAC Reference */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/30 p-4">
        <h4 className="text-xs font-semibold text-mission-400 mb-3">Role Permissions</h4>
        <div className="grid grid-cols-4 gap-3 text-[10px]">
          {[
            { role: "Admin", desc: "Full access: manage org, users, workflows, MCP, reports", color: "text-agent-rose" },
            { role: "Editor", desc: "Create/edit workflows, execute, generate reports, resolve approvals", color: "text-agent-amber" },
            { role: "Viewer", desc: "Read-only: view workflows, dashboards, audit trail", color: "text-mission-300" },
            { role: "Auditor", desc: "Read audit trail, generate reports, view all data", color: "text-agent-violet" },
          ].map((r) => (
            <div key={r.role} className="rounded bg-mission-800/30 p-3">
              <div className={`font-medium mb-1 ${r.color}`}>{r.role}</div>
              <div className="text-mission-500">{r.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
