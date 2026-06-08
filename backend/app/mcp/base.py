"""
MCP Base Adapter — pluggable connector framework for external systems.
Each adapter provides tool discovery, connection management, and health checks.
Agents never call systems directly — they only use MCP tools.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MCPTool(BaseModel):
    """Schema for a discovered/registered MCP tool."""
    name: str
    description: str = ""
    parameters: dict = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class MCPServerInfo(BaseModel):
    """Metadata about an MCP server connection."""
    name: str
    adapter_type: str
    status: AdapterStatus = AdapterStatus.DISCONNECTED
    tools: list[MCPTool] = Field(default_factory=list)
    connection_config: dict = Field(default_factory=dict)
    last_health_check: Optional[str] = None
    error_message: Optional[str] = None


class BaseAdapter(ABC):
    """
    Abstract base for all MCP system adapters.
    Subclasses implement connect(), discover_tools(), and health_check().
    """

    adapter_type: str = "base"

    def __init__(self, config: dict):
        self.config = config
        self.status = AdapterStatus.DISCONNECTED
        self.tools: list[MCPTool] = []
        self.error: Optional[str] = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the external system. Returns True on success."""
        ...

    @abstractmethod
    async def discover_tools(self) -> list[MCPTool]:
        """Discover available tools/capabilities from the external system."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the connection is alive. Returns True if healthy."""
        ...

    @abstractmethod
    async def execute(self, tool_name: str, params: dict) -> Any:
        """Execute a tool against the external system."""
        ...

    async def initialize(self) -> bool:
        """Full initialization: connect + discover tools."""
        self.status = AdapterStatus.CONNECTING
        try:
            if await self.connect():
                self.tools = await self.discover_tools()
                self.status = AdapterStatus.CONNECTED
                self.error = None
                logger.info(f"[MCP] {self.adapter_type} initialized with {len(self.tools)} tools")
                return True
        except Exception as e:
            self.status = AdapterStatus.ERROR
            self.error = str(e)
            logger.error(f"[MCP] {self.adapter_type} init failed: {e}")
        return False

    def get_info(self, name: str) -> MCPServerInfo:
        """Return server metadata."""
        return MCPServerInfo(
            name=name,
            adapter_type=self.adapter_type,
            status=self.status,
            tools=self.tools,
            connection_config=self.config,
            error_message=self.error,
        )

    def _redact_config(self) -> dict:
        """Remove sensitive fields from config for display."""
        safe = dict(self.config)
        for key in ("password", "token", "secret", "api_key", "private_key"):
            if key in safe:
                safe[key] = "***"
        return safe
