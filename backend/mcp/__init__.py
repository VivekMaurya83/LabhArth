"""
LabhArth AI — MCP Package
============================
Model Context Protocol server and tool definitions.
Provides standardized tool access for ADK agents.
"""

from backend.mcp.server import MCPServer, create_mcp_server

__all__ = ["MCPServer", "create_mcp_server"]
