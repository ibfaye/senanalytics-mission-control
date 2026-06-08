"""MCP API — manage MCP server connections and execute tools."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.mcp.registry import mcp_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


class RegisterServerRequest(BaseModel):
    name: str
    adapter_type: str
    connection_config: dict = {}


class ExecuteToolRequest(BaseModel):
    server_name: str
    tool_name: str
    params: dict = {}


@router.get("/adapters")
async def list_adapter_types():
    """List available MCP adapter types (Snowflake, AWS, etc.)."""
    return {
        "adapters": [
            {"type": t, "label": t.replace("_", " ").title()}
            for t in mcp_registry.available_adapter_types
        ]
    }


@router.get("/servers")
async def list_servers():
    """List all registered MCP servers with status and tools."""
    return mcp_registry.list_servers()


@router.post("/servers")
async def register_server(body: RegisterServerRequest):
    """Register and initialize a new MCP server."""
    success = await mcp_registry.register_server(
        body.name, body.adapter_type, body.connection_config
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register server")
    server = mcp_registry.get_server(body.name)
    if server:
        return server.get_info(body.name)
    raise HTTPException(status_code=500, detail="Server registered but not found")


@router.delete("/servers/{server_name}")
async def unregister_server(server_name: str):
    """Remove an MCP server."""
    if not await mcp_registry.unregister_server(server_name):
        raise HTTPException(status_code=404, detail="Server not found")
    return {"message": f"Server '{server_name}' unregistered"}


@router.get("/servers/{server_name}")
async def get_server(server_name: str):
    """Get details for a specific MCP server."""
    server = mcp_registry.get_server(server_name)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server.get_info(server_name)


@router.get("/tools")
async def list_all_tools():
    """List all tools across all registered MCP servers."""
    return mcp_registry.list_all_tools()


@router.post("/tools/execute")
async def execute_tool(body: ExecuteToolRequest):
    """Execute a tool on a registered MCP server."""
    try:
        result = await mcp_registry.execute_tool(
            body.server_name, body.tool_name, body.params
        )
        return {"server": body.server_name, "tool": body.tool_name, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check_all():
    """Run health checks on all MCP servers."""
    return await mcp_registry.health_check_all()
