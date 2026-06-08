"""
AWS MCP Adapter — S3, RDS, Glue, Athena discovery and scanning.
"""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

AWS_TOOLS = [
    MCPTool(name="aws.list_s3_buckets", description="List all S3 buckets in the account"),
    MCPTool(name="aws.list_rds_instances", description="List RDS database instances"),
    MCPTool(name="aws.list_glue_catalogs", description="List Glue Data Catalog databases"),
    MCPTool(name="aws.list_glue_tables", description="List tables in a Glue database",
            parameters={"database": {"type": "string"}}, required=["database"]),
    MCPTool(name="aws.check_s3_encryption", description="Check S3 bucket encryption status",
            parameters={"bucket": {"type": "string"}}, required=["bucket"]),
    MCPTool(name="aws.check_iam_roles", description="List IAM roles with data access"),
    MCPTool(name="aws.run_athena_query", description="Execute an Athena SQL query",
            parameters={"query": {"type": "string"}, "database": {"type": "string"}},
            required=["query", "database"]),
]


class AwsAdapter(BaseAdapter):
    adapter_type = "aws"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return AWS_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "aws.list_s3_buckets": lambda: {
                "buckets": [
                    {"name": "customer-data-prod", "region": "us-east-1", "encrypted": True},
                    {"name": "analytics-raw", "region": "us-east-1", "encrypted": False},
                    {"name": "archive-logs", "region": "eu-west-1", "encrypted": True},
                ]
            },
            "aws.list_rds_instances": lambda: {
                "instances": [
                    {"id": "prod-db-01", "engine": "postgres", "encrypted": True, "publicly_accessible": False},
                    {"id": "analytics-reader", "engine": "postgres", "encrypted": True, "publicly_accessible": False},
                ]
            },
            "aws.list_glue_catalogs": lambda: {"databases": ["customer_catalog", "analytics_catalog"]},
            "aws.list_glue_tables": lambda: {
                "tables": ["customers", "orders", "events", "audit_trail"]
            },
            "aws.check_s3_encryption": lambda: {
                "bucket": params.get("bucket", "?"),
                "encrypted": False,
                "reason": "Default encryption not enabled",
            },
            "aws.check_iam_roles": lambda: {
                "roles": [
                    {"name": "DataEngineer", "attached_policies": 3, "has_s3_access": True},
                    {"name": "AnalystReadOnly", "attached_policies": 1, "has_s3_access": True},
                    {"name": "AdminFullAccess", "attached_policies": 5, "has_s3_access": True},
                ]
            },
            "aws.run_athena_query": lambda: {"rows": 100, "runtime_ms": 2500},
        }
        handler = tool_map.get(tool_name)
        if handler:
            return handler()
        raise ValueError(f"Unknown AWS tool: {tool_name}")
