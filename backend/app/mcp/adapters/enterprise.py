"""Databricks + SQL Server + ServiceNow + Power BI + Purview adapters."""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

# ─── Databricks ───────────────────────────────────────────

DATABRICKS_TOOLS = [
    MCPTool(name="databricks.list_clusters", description="List Databricks compute clusters"),
    MCPTool(name="databricks.list_jobs", description="List scheduled jobs and their status"),
    MCPTool(name="databricks.list_tables", description="List tables in Unity Catalog",
            parameters={"catalog": {"type": "string"}, "schema": {"type": "string"}},
            required=["catalog", "schema"]),
    MCPTool(name="databricks.run_sql", description="Execute SQL via Databricks SQL Warehouse",
            parameters={"query": {"type": "string"}}, required=["query"]),
    MCPTool(name="databricks.get_table_lineage", description="Get Unity Catalog lineage for a table",
            parameters={"table": {"type": "string"}}, required=["table"]),
]


class DatabricksAdapter(BaseAdapter):
    adapter_type = "databricks"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return DATABRICKS_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "databricks.list_clusters": lambda: {"clusters": [{"name": "Analytics", "state": "RUNNING"}, {"name": "ETL", "state": "TERMINATED"}]},
            "databricks.list_jobs": lambda: {"jobs": [{"name": "daily_etl", "status": "SUCCESS"}, {"name": "gdpr_scan", "status": "PENDING"}]},
            "databricks.list_tables": lambda: {"tables": ["customers", "orders", "products", "audit_log"]},
            "databricks.run_sql": lambda: {"rows": 10000, "runtime_ms": 3200},
            "databricks.get_table_lineage": lambda: {"table": params.get("table"), "upstream": ["raw_events"], "downstream": ["customer_360", "analytics_report"]},
        }
        handler = tool_map.get(tool_name)
        return handler() if handler else {"error": f"Unknown tool: {tool_name}"}


# ─── SQL Server ───────────────────────────────────────────

SQLSERVER_TOOLS = [
    MCPTool(name="sqlserver.list_databases", description="List databases on SQL Server"),
    MCPTool(name="sqlserver.list_tables", description="List tables in a database", parameters={"database": {"type": "string"}}, required=["database"]),
    MCPTool(name="sqlserver.describe_table", description="Get column info", parameters={"table": {"type": "string"}}, required=["table"]),
    MCPTool(name="sqlserver.run_query", description="Execute a SELECT query", parameters={"query": {"type": "string"}}, required=["query"]),
]


class SqlServerAdapter(BaseAdapter):
    adapter_type = "sqlserver"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return SQLSERVER_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "sqlserver.list_databases": lambda: {"databases": ["MarketingDB", "SalesDB", "AuditDB"]},
            "sqlserver.list_tables": lambda: {"tables": ["contacts", "campaigns", "leads"]},
            "sqlserver.describe_table": lambda: {"columns": [{"name": "email", "type": "NVARCHAR", "pii": True}, {"name": "id", "type": "INT", "pii": False}]},
            "sqlserver.run_query": lambda: {"rows": 500, "sample": []},
        }
        handler = tool_map.get(tool_name)
        return handler() if handler else {"error": f"Unknown tool: {tool_name}"}


# ─── ServiceNow ───────────────────────────────────────────

SERVICENOW_TOOLS = [
    MCPTool(name="servicenow.list_incidents", description="List open incidents"),
    MCPTool(name="servicenow.search_cmdb", description="Search CMDB configuration items", parameters={"query": {"type": "string"}}, required=["query"]),
    MCPTool(name="servicenow.get_change_requests", description="Get open change requests"),
    MCPTool(name="servicenow.create_incident", description="Create a new incident",
            parameters={"short_description": {"type": "string"}, "category": {"type": "string"}},
            required=["short_description"]),
]


class ServiceNowAdapter(BaseAdapter):
    adapter_type = "servicenow"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return SERVICENOW_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "servicenow.list_incidents": lambda: {"incidents": [{"number": "INC001", "state": "Open", "priority": "1-Critical"}, {"number": "INC002", "state": "In Progress", "priority": "2-High"}]},
            "servicenow.search_cmdb": lambda: {"items": [{"name": "prod-db-01", "class": "Database"}, {"name": "analytics-cluster", "class": "Server"}]},
            "servicenow.get_change_requests": lambda: {"changes": [{"number": "CHG001", "state": "Pending Approval"}, {"number": "CHG002", "state": "Scheduled"}]},
            "servicenow.create_incident": lambda: {"created": True, "number": "INC100", "sys_id": "abc123"},
        }
        handler = tool_map.get(tool_name)
        return handler() if handler else {"error": f"Unknown tool: {tool_name}"}


# ─── Power BI ─────────────────────────────────────────────

POWERBI_TOOLS = [
    MCPTool(name="powerbi.list_workspaces", description="List Power BI workspaces"),
    MCPTool(name="powerbi.list_reports", description="List reports in a workspace", parameters={"workspace": {"type": "string"}}, required=["workspace"]),
    MCPTool(name="powerbi.list_datasets", description="List datasets with refresh status"),
    MCPTool(name="powerbi.get_dataset_sources", description="Get data sources for a dataset",
            parameters={"dataset_id": {"type": "string"}}, required=["dataset_id"]),
]


class PowerBIAdapter(BaseAdapter):
    adapter_type = "powerbi"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return POWERBI_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "powerbi.list_workspaces": lambda: {"workspaces": ["Governance Reports", "Security Dashboard", "Executive Analytics"]},
            "powerbi.list_reports": lambda: {"reports": [{"name": "GDPR Compliance Status", "id": "rpt-001"}, {"name": "Risk Heatmap", "id": "rpt-002"}]},
            "powerbi.list_datasets": lambda: {"datasets": [{"name": "Customer Data", "refresh_status": "Success"}, {"name": "Audit Logs", "refresh_status": "Failed"}]},
            "powerbi.get_dataset_sources": lambda: {"sources": [{"type": "SQL", "server": "prod-db-01", "database": "customers"}]},
        }
        handler = tool_map.get(tool_name)
        return handler() if handler else {"error": f"Unknown tool: {tool_name}"}


# ─── Microsoft Purview ────────────────────────────────────

PURVIEW_TOOLS = [
    MCPTool(name="purview.search_assets", description="Search Purview Data Catalog", parameters={"keyword": {"type": "string"}}, required=["keyword"]),
    MCPTool(name="purview.get_classifications", description="Get all classifications for an asset",
            parameters={"asset_id": {"type": "string"}}, required=["asset_id"]),
    MCPTool(name="purview.get_lineage", description="Get data lineage for an asset",
            parameters={"asset_id": {"type": "string"}}, required=["asset_id"]),
    MCPTool(name="purview.scan_status", description="Get latest scan status for a data source",
            parameters={"source_name": {"type": "string"}}, required=["source_name"]),
]


class PurviewAdapter(BaseAdapter):
    adapter_type = "purview"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return PURVIEW_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "purview.search_assets": lambda: {"assets": [{"name": "customers", "type": "Azure SQL Table", "classification": "PII"}, {"name": "orders", "type": "Azure SQL Table"}]},
            "purview.get_classifications": lambda: {"classifications": [{"column": "email", "type": "PII-Email"}, {"column": "phone", "type": "PII-Phone"}, {"column": "ssn", "type": "PII-SSN"}]},
            "purview.get_lineage": lambda: {"upstream": ["raw_customers.csv"], "downstream": ["customer_360_view", "monthly_report"]},
            "purview.scan_status": lambda: {"source": params.get("source_name"), "last_scan": "2026-06-07T08:00:00Z", "status": "Completed", "assets_scanned": 150},
        }
        handler = tool_map.get(tool_name)
        return handler() if handler else {"error": f"Unknown tool: {tool_name}"}
