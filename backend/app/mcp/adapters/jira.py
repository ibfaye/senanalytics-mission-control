"""
Jira MCP Adapter — issue tracking, project management, compliance workflow integration.
"""

import logging
from app.mcp.base import BaseAdapter, MCPTool

logger = logging.getLogger(__name__)

JIRA_TOOLS = [
    MCPTool(name="jira.list_projects", description="List all accessible Jira projects"),
    MCPTool(name="jira.search_issues", description="Search issues by JQL query",
            parameters={"jql": {"type": "string"}}, required=["jql"]),
    MCPTool(name="jira.get_issue", description="Get a single issue by key",
            parameters={"key": {"type": "string"}}, required=["key"]),
    MCPTool(name="jira.get_compliance_tasks", description="Get open compliance/GRC tasks"),
    MCPTool(name="jira.create_issue", description="Create a new issue",
            parameters={
                "project": {"type": "string"},
                "summary": {"type": "string"},
                "description": {"type": "string"},
                "issue_type": {"type": "string", "description": "Bug, Task, Story, etc."},
            },
            required=["project", "summary", "issue_type"],
    ),
    MCPTool(name="jira.get_audit_trail", description="Get recent issue activity for audit purposes",
            parameters={"project": {"type": "string"}}, required=["project"]),
]


class JiraAdapter(BaseAdapter):
    adapter_type = "jira"

    async def connect(self) -> bool:
        logger.info(f"[{self.adapter_type}] Connected (demo mode)")
        return True
    

    async def discover_tools(self) -> list[MCPTool]:
        return JIRA_TOOLS

    async def health_check(self) -> bool:
        return self.status.value == "connected"

    async def execute(self, tool_name: str, params: dict) -> dict:
        tool_map = {
            "jira.list_projects": lambda: {
                "projects": [
                    {"key": "GRC", "name": "Governance Risk & Compliance"},
                    {"key": "SEC", "name": "Security Operations"},
                    {"key": "DATA", "name": "Data Engineering"},
                ]
            },
            "jira.search_issues": lambda: {
                "total": 12,
                "issues": [
                    {"key": "GRC-101", "summary": "PII encryption audit findings"},
                    {"key": "GRC-102", "summary": "GDPR Article 32 compliance gap"},
                    {"key": "SEC-201", "summary": "IAM role review for analytics pipeline"},
                ]
            },
            "jira.get_issue": lambda: {
                "key": params.get("key", "?"),
                "summary": "Compliance remediation task",
                "status": "In Progress",
                "assignee": "ibfaye",
                "priority": "High",
            },
            "jira.get_compliance_tasks": lambda: {
                "tasks": [
                    {"key": "GRC-101", "status": "Open", "priority": "Critical"},
                    {"key": "GRC-103", "status": "In Progress", "priority": "High"},
                    {"key": "GRC-105", "status": "Open", "priority": "Medium"},
                ]
            },
            "jira.create_issue": lambda: {
                "created": True,
                "key": "GRC-200",
                "url": f"{self.config.get('url', '')}/browse/GRC-200",
            },
            "jira.get_audit_trail": lambda: {
                "project": params.get("project", "?"),
                "recent_activity": [
                    {"issue": "GRC-101", "action": "status_changed", "from": "Open", "to": "In Progress", "date": "2026-06-07"},
                    {"issue": "SEC-201", "action": "commented", "author": "ibfaye", "date": "2026-06-06"},
                ]
            },
        }
        handler = tool_map.get(tool_name)
        if handler:
            return handler()
        raise ValueError(f"Unknown Jira tool: {tool_name}")
