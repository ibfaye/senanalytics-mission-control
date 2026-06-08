"""
PostgreSQL MCP Adapter — direct database schema discovery and query execution.
"""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

POSTGRES_TOOLS = [
    MCPTool(name="pg.list_databases", description="List all databases on the PostgreSQL server"),
    MCPTool(name="pg.list_schemas", description="List schemas in a database",
            parameters={"database": {"type": "string"}}, required=["database"]),
    MCPTool(name="pg.list_tables", description="List tables in a schema",
            parameters={"schema": {"type": "string"}}, required=["schema"]),
    MCPTool(name="pg.describe_table", description="Get column definitions with types and constraints",
            parameters={"schema": {"type": "string"}, "table": {"type": "string"}},
            required=["schema", "table"]),
    MCPTool(name="pg.run_query", description="Execute a read-only SQL query",
            parameters={"query": {"type": "string"}}, required=["query"]),
    MCPTool(name="pg.check_encryption", description="Check if encryption is enabled for a table",
            parameters={"table": {"type": "string"}}, required=["table"]),
]


class PostgresAdapter(BaseAdapter):
    adapter_type = "postgres"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return POSTGRES_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "pg.list_databases": lambda: {"databases": ["senanalytics", "customers_db", "analytics"]},
            "pg.list_schemas": lambda: {"schemas": ["public", "governance", "audit"]},
            "pg.list_tables": lambda: {"tables": ["customers", "workflows", "executions", "audit_logs"]},
            "pg.describe_table": lambda: {
                "columns": [
                    {"name": "id", "type": "UUID", "nullable": False, "pii": False},
                    {"name": "email", "type": "VARCHAR(255)", "nullable": False, "pii": True},
                    {"name": "phone", "type": "VARCHAR(20)", "nullable": True, "pii": True},
                    {"name": "encrypted_at_rest", "type": "BOOLEAN", "nullable": False},
                ]
            },
            "pg.run_query": lambda: {"rows": 5000, "sample": []},
            "pg.check_encryption": lambda: {
                "table": params.get("table", "?"),
                "encryption_enabled": True,
                "method": "pg_tde",
                "key_rotation_days": 90,
            },
        }
        handler = tool_map.get(tool_name)
        if handler:
            return handler()
        raise ValueError(f"Unknown Postgres tool: {tool_name}")
