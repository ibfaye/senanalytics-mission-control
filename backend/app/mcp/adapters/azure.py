"""
Azure MCP Adapter — Blob Storage, SQL Database, Purview, Synapse discovery.
"""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

AZURE_TOOLS = [
    MCPTool(name="azure.list_storage_accounts", description="List Azure Storage accounts"),
    MCPTool(name="azure.list_sql_databases", description="List Azure SQL databases"),
    MCPTool(name="azure.list_purview_assets", description="List assets registered in Microsoft Purview"),
    MCPTool(name="azure.search_purview_glossary", description="Search Purview glossary terms",
            parameters={"term": {"type": "string"}}, required=["term"]),
    MCPTool(name="azure.check_purview_classifications", description="Get Purview classifications for an asset",
            parameters={"asset_name": {"type": "string"}}, required=["asset_name"]),
    MCPTool(name="azure.list_synapse_pipelines", description="List Synapse Analytics pipelines"),
    MCPTool(name="azure.check_key_vault_secrets", description="List Key Vault secrets (names only)"),
]


class AzureAdapter(BaseAdapter):
    adapter_type = "azure"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return AZURE_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "azure.list_storage_accounts": lambda: {
                "accounts": ["sacustomerdata", "saanalyticsraw", "saarchive"]
            },
            "azure.list_sql_databases": lambda: {
                "databases": ["CustomerDB", "AnalyticsDB", "GovernanceDB"]
            },
            "azure.list_purview_assets": lambda: {
                "assets": [
                    {"name": "customers", "type": "Azure SQL Table", "classified": True},
                    {"name": "orders", "type": "Azure SQL Table", "classified": False},
                    {"name": "analytics_events", "type": "Azure Data Lake", "classified": True},
                ]
            },
            "azure.search_purview_glossary": lambda: {
                "matches": [
                    {"term": "PII", "definition": "Personally Identifiable Information"},
                    {"term": "GDPR", "definition": "General Data Protection Regulation"},
                ]
            },
            "azure.check_purview_classifications": lambda: {
                "asset": params.get("asset_name", "?"),
                "classifications": [
                    {"column": "email", "classification": "PII-Email", "confidence": 0.95},
                    {"column": "phone", "classification": "PII-Phone", "confidence": 0.92},
                ]
            },
            "azure.list_synapse_pipelines": lambda: {
                "pipelines": ["ETL_Customer_Load", "GDPR_Compliance_Scan", "Daily_Audit_Export"]
            },
            "azure.check_key_vault_secrets": lambda: {
                "secrets": ["db-password-prod", "api-key-analytics", "encryption-key-2024"]
            },
        }
        handler = tool_map.get(tool_name)
        if handler:
            return handler()
        raise ValueError(f"Unknown Azure tool: {tool_name}")
