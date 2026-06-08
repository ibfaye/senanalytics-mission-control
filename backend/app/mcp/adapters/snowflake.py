"""
Snowflake MCP Adapter — data warehouse discovery, schema analysis, query execution.
"""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

SNOWFLAKE_TOOLS = [
    MCPTool(
        name="snowflake.list_databases",
        description="List all accessible databases in Snowflake",
        parameters={"filter": {"type": "string", "description": "Optional name filter"}},
    ),
    MCPTool(
        name="snowflake.list_schemas",
        description="List schemas in a Snowflake database",
        parameters={"database": {"type": "string", "description": "Database name"}},
        required=["database"],
    ),
    MCPTool(
        name="snowflake.list_tables",
        description="List tables in a Snowflake schema",
        parameters={
            "database": {"type": "string"},
            "schema": {"type": "string"},
        },
        required=["database", "schema"],
    ),
    MCPTool(
        name="snowflake.describe_table",
        description="Get column definitions for a Snowflake table",
        parameters={
            "database": {"type": "string"},
            "schema": {"type": "string"},
            "table": {"type": "string"},
        },
        required=["database", "schema", "table"],
    ),
    MCPTool(
        name="snowflake.run_query",
        description="Execute a read-only SQL query against Snowflake",
        parameters={"query": {"type": "string", "description": "SQL SELECT query"}},
        required=["query"],
    ),
    MCPTool(
        name="snowflake.get_row_count",
        description="Get approximate row count for a table",
        parameters={
            "database": {"type": "string"},
            "schema": {"type": "string"},
            "table": {"type": "string"},
        },
        required=["database", "schema", "table"],
    ),
]


class SnowflakeAdapter(BaseAdapter):
    adapter_type = "snowflake"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return SNOWFLAKE_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "snowflake.list_databases": lambda: {
                "databases": ["PROD_DB", "ANALYTICS_DB", "STAGING_DB", "CUSTOMER_360"]
            },
            "snowflake.list_schemas": lambda: {
                "schemas": ["PUBLIC", "RAW", "CURATED", "GOVERNANCE"]
            },
            "snowflake.list_tables": lambda: {
                "tables": ["customers", "orders", "products", "analytics_events"]
            },
            "snowflake.describe_table": lambda: {
                "columns": [
                    {"name": "id", "type": "NUMBER", "nullable": False},
                    {"name": "email", "type": "VARCHAR", "nullable": True, "pii": True},
                    {"name": "full_name", "type": "VARCHAR", "nullable": True, "pii": True},
                    {"name": "created_at", "type": "TIMESTAMP_NTZ", "nullable": False},
                ]
            },
            "snowflake.run_query": lambda: {
                "rows": 1500000, "columns": 12, "sample": [{"id": 1, "email": "***@example.com"}]
            },
            "snowflake.get_row_count": lambda: {"table": params.get("table", "?"), "row_count": 1500000},
        }
        handler = tool_map.get(tool_name)
        if handler:
            return handler()
        raise ValueError(f"Unknown Snowflake tool: {tool_name}")
