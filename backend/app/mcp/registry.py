"""
MCP Registry — manages adapter lifecycle, tool discovery, and execution.
Acts as the single gateway between agents and external systems.
"""

import logging
from typing import Optional, Any
from app.mcp.base import BaseAdapter, MCPServerInfo, MCPTool
from app.mcp.adapters import (
    SnowflakeAdapter,
    PostgresAdapter,
    AwsAdapter,
    AzureAdapter,
    JiraAdapter,
    DatabricksAdapter,
    SqlServerAdapter,
    ServiceNowAdapter,
    PowerBIAdapter,
    PurviewAdapter,
)

logger = logging.getLogger(__name__)

# Adapter factory
_ADAPTER_CLASSES: dict[str, type[BaseAdapter]] = {
    "snowflake": SnowflakeAdapter,
    "postgres": PostgresAdapter,
    "aws": AwsAdapter,
    "azure": AzureAdapter,
    "jira": JiraAdapter,
    "databricks": DatabricksAdapter,
    "sqlserver": SqlServerAdapter,
    "servicenow": ServiceNowAdapter,
    "powerbi": PowerBIAdapter,
    "purview": PurviewAdapter,
}


class MCPRegistry:
    """Manages MCP server connections, tool discovery, and agent-tool routing."""

    def __init__(self):
        self._servers: dict[str, BaseAdapter] = {}
        self._server_configs: dict[str, dict] = {}

    @property
    def available_adapter_types(self) -> list[str]:
        return list(_ADAPTER_CLASSES.keys())

    async def register_server(self, name: str, adapter_type: str, config: dict) -> bool:
        """Register and initialize an MCP server."""
        adapter_cls = _ADAPTER_CLASSES.get(adapter_type)
        if not adapter_cls:
            logger.error(f"[MCP] Unknown adapter type: {adapter_type}")
            return False

        adapter = adapter_cls(config)
        success = await adapter.initialize()
        self._servers[name] = adapter
        self._server_configs[name] = config

        if success:
            logger.info(f"[MCP] Registered server '{name}' ({adapter_type}) with {len(adapter.tools)} tools")
        return success

    async def unregister_server(self, name: str) -> bool:
        """Remove an MCP server."""
        if name in self._servers:
            del self._servers[name]
            self._server_configs.pop(name, None)
            return True
        return False

    def get_server(self, name: str) -> Optional[BaseAdapter]:
        """Get an adapter by server name."""
        return self._servers.get(name)

    def list_servers(self) -> list[MCPServerInfo]:
        """List all registered servers with status."""
        return [
            adapter.get_info(name)
            for name, adapter in self._servers.items()
        ]

    def list_all_tools(self) -> list[dict]:
        """List all tools across all connected servers."""
        tools = []
        for name, adapter in self._servers.items():
            for tool in adapter.tools:
                tools.append({
                    "server": name,
                    "adapter_type": adapter.adapter_type,
                    "tool_name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                })
        return tools

    async def execute_tool(self, server_name: str, tool_name: str, params: dict) -> Any:
        """Execute a tool on a specific server."""
        adapter = self._servers.get(server_name)
        if not adapter:
            raise ValueError(f"Server '{server_name}' not found")
        return await adapter.execute(tool_name, params)

    async def health_check_all(self) -> dict[str, bool]:
        """Run health checks on all registered servers."""
        results = {}
        for name, adapter in self._servers.items():
            results[name] = await adapter.health_check()
        return results


# Singleton
mcp_registry = MCPRegistry()
