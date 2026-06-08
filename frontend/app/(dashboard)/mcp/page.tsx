"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import {
  Server,
  Plug,
  CheckCircle2,
  XCircle,
  Wrench,
  Loader2,
} from "lucide-react";

const adapterColors: Record<string, string> = {
  snowflake: "text-cyan-400",
  postgres: "text-violet-400",
  aws: "text-amber-400",
  azure: "text-blue-400",
  jira: "text-blue-500",
  databricks: "text-orange-400",
  sqlserver: "text-red-400",
  servicenow: "text-green-400",
  powerbi: "text-yellow-400",
  purview: "text-purple-400",
};

export default function MCPPage() {
  const qc = useQueryClient();

  const { data: servers, isLoading } = useQuery({
    queryKey: ["mcp-servers"],
    queryFn: () =>
      api.get<
        {
          name: string;
          adapter_type: string;
          status: string;
          tools: { name: string; description: string }[];
          error_message?: string;
        }[]
      >("/mcp/servers"),
    refetchInterval: 15_000,
  });

  const connectMutation = useMutation({
    mutationFn: (data: { name: string; adapter_type: string }) =>
      api.post("/mcp/servers", {
        name: data.name,
        adapter_type: data.adapter_type,
        connection_config: {},
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mcp-servers"] }),
  });

  const disconnectMutation = useMutation({
    mutationFn: (name: string) => api.delete(`/mcp/servers/${name}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mcp-servers"] }),
  });

  const { data: adapterTypes } = useQuery({
    queryKey: ["mcp-adapters"],
    queryFn: () =>
      api.get<{ adapters: { type: string; label: string }[] }>("/mcp/adapters"),
    staleTime: Infinity,
  });

  const availableAdapters =
    adapterTypes?.adapters?.filter(
      (a) => !servers?.some((s) => s.adapter_type === a.type),
    ) || [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-mission-200">
          MCP Server Registry
        </h3>
        <span className="text-[10px] text-mission-500 font-mono">
          Pluggable Tool Adapters
        </span>
      </div>

      {/* Connected Servers */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <div className="col-span-full p-8 text-center">
            <Loader2 className="mx-auto h-5 w-5 text-mission-500 animate-spin" />
          </div>
        ) : servers && servers.length > 0 ? (
          servers.map((server) => (
            <div
              key={server.name}
              className={`rounded-lg border p-4 transition-colors
                ${
                  server.status === "connected"
                    ? "border-emerald-800 bg-emerald-950/20"
                    : server.status === "error"
                      ? "border-red-800 bg-red-950/20"
                      : "border-mission-800 bg-mission-900/50"
                }`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <Server
                      className={`h-4 w-4 ${adapterColors[server.adapter_type] || "text-mission-400"}`}
                    />
                    <span className="text-sm font-medium text-mission-200">
                      {server.name}
                    </span>
                  </div>
                  <span className="text-[10px] text-mission-500 font-mono mt-0.5 block">
                    {server.adapter_type}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {server.status === "connected" ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  ) : server.status === "error" ? (
                    <XCircle className="h-4 w-4 text-red-400" />
                  ) : (
                    <Loader2 className="h-4 w-4 text-mission-500 animate-spin" />
                  )}
                </div>
              </div>

              {/* Tools */}
              {server.tools && server.tools.length > 0 && (
                <div className="mb-3">
                  <div className="flex flex-wrap gap-1">
                    {server.tools.slice(0, 6).map((tool) => (
                      <span
                        key={tool.name}
                        className="rounded bg-mission-800 px-1.5 py-0.5 text-[9px] text-mission-400 font-mono"
                        title={tool.description}>
                        {tool.name}
                      </span>
                    ))}
                    {server.tools.length > 6 && (
                      <span className="text-[9px] text-mission-600">
                        +{server.tools.length - 6} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {server.error_message && (
                <p className="text-[10px] text-red-400 mb-2">
                  {server.error_message}
                </p>
              )}

              <button
                onClick={() => disconnectMutation.mutate(server.name)}
                className="text-[10px] text-mission-500 hover:text-red-400 transition-colors">
                Disconnect
              </button>
            </div>
          ))
        ) : (
          <div className="col-span-full rounded-lg border border-dashed border-mission-700 p-12 text-center">
            <Plug className="mx-auto h-8 w-8 text-mission-600 mb-3" />
            <p className="text-sm text-mission-500">
              No MCP servers connected
            </p>
            <p className="text-xs text-mission-600 mt-1">
              Connect a server below to enable tool discovery
            </p>
          </div>
        )}
      </div>

      {/* Available Adapters */}
      {availableAdapters.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-mission-400 mb-3">
            Available Adapters
          </h4>
          <div className="flex flex-wrap gap-2">
            {availableAdapters.map((adapter) => (
              <button
                key={adapter.type}
                onClick={() =>
                  connectMutation.mutate({
                    name: adapter.type,
                    adapter_type: adapter.type,
                  })
                }
                disabled={connectMutation.isPending}
                className="flex items-center gap-1.5 rounded-md border border-mission-800 bg-mission-900/50 px-3 py-2 text-xs text-mission-300 hover:border-mission-700 hover:text-mission-100 transition-colors disabled:opacity-50">
                <Plug
                  className={`h-3 w-3 ${adapterColors[adapter.type] || ""}`}
                />
                {adapter.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* All 10 adapters listed */}
      <div className="rounded-lg border border-mission-800 bg-mission-900/30 p-4">
        <h4 className="text-xs font-semibold text-mission-400 mb-3">
          All Supported Systems
        </h4>
        <div className="grid grid-cols-5 gap-3">
          {[
            { type: "snowflake", label: "Snowflake" },
            { type: "databricks", label: "Databricks" },
            { type: "postgres", label: "PostgreSQL" },
            { type: "sqlserver", label: "SQL Server" },
            { type: "jira", label: "Jira" },
            { type: "servicenow", label: "ServiceNow" },
            { type: "powerbi", label: "Power BI" },
            { type: "purview", label: "MS Purview" },
            { type: "aws", label: "AWS" },
            { type: "azure", label: "Azure" },
          ].map((sys) => (
            <div
              key={sys.type}
              className={`rounded-md border border-mission-800 px-3 py-2 text-center
                ${servers?.some((s) => s.adapter_type === sys.type) ? "bg-emerald-950/20 border-emerald-800" : "bg-mission-900/30"}`}>
              <div
                className={`text-lg mb-1 ${adapterColors[sys.type] || ""}`}>
                <Wrench className="h-4 w-4 mx-auto" />
              </div>
              <span className="text-[10px] text-mission-400">{sys.label}</span>
              {servers?.some((s) => s.adapter_type === sys.type) && (
                <div className="mt-1">
                  <CheckCircle2 className="h-3 w-3 text-emerald-400 mx-auto" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
