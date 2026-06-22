"""
LabhArth AI — MCP Server
===========================
Model Context Protocol server that exposes tools to ADK agents.

The MCP server runs as a separate process and provides a standardized
interface for agents to invoke tools like search_schemes, get_scheme_details,
and check_eligibility.
"""

from backend.utils.config import get_settings
from backend.utils.logger import logger


class MCPServer:
    """
    MCP Server for LabhArth AI.

    Registers and serves tools that ADK agents can invoke
    via the Model Context Protocol.

    Tools registered:
    - search_schemes: Semantic + structured scheme search
    - get_scheme_details: Full scheme information retrieval
    - check_eligibility: Profile-based eligibility determination
    """

    def __init__(self):
        self.settings = get_settings()
        self.tools = {}
        logger.info("MCP Server initialized")

    def register_tools(self) -> None:
        """Register all MCP tools."""
        from backend.mcp.tools import (
            check_eligibility,
            get_scheme_details,
            search_schemes,
        )

        self.tools = {
            "search_schemes": search_schemes,
            "get_scheme_details": get_scheme_details,
            "check_eligibility": check_eligibility,
        }
        logger.info(f"Registered {len(self.tools)} MCP tools: {list(self.tools.keys())}")

    async def start(self) -> None:
        """
        Start the MCP server.

        TODO: Implement with the MCP SDK when integrating with ADK.
        The server will listen for tool invocation requests from agents.
        """
        self.register_tools()
        logger.info(
            f"MCP Server starting on {self.settings.mcp_server_host}:{self.settings.mcp_server_port}"
        )
        # TODO: Implement MCP server startup with mcp SDK
        pass


def create_mcp_server() -> MCPServer:
    """Factory function to create and configure an MCP server instance."""
    server = MCPServer()
    server.register_tools()
    return server
