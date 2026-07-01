"""
LabhArth AI — MCP Server
===========================
Model Context Protocol server that exposes tools to ADK agents.

The MCP server runs as a separate process and provides a standardized
interface for agents to invoke tools like search_schemes, get_scheme_details,
and check_eligibility.
"""

import logging
import os
import sys

# Robust redirector to send all text writes/prints to stderr,
# preserving the original stdout.buffer for the MCP stdio JSON-RPC stream.
class StdoutRedirector:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = original_stdout.buffer

    def write(self, data):
        sys.stderr.write(data)

    def flush(self):
        sys.stderr.flush()

    def __getattr__(self, name):
        return getattr(self.original_stdout, name)

# Apply redirection immediately
sys.stdout = StdoutRedirector(sys.stdout)

# Configure file logging for the MCP process to prevent standard streams
# from filling buffers and deadlocking stdio communication.
def configure_file_logging():
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mcp_server.log")

    # Reconfigure loggers to write to file
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # Reconfigure root and labharth loggers
    for logger_name in ["", "labharth"]:
        l = logging.getLogger(logger_name)
        for handler in l.handlers[:]:
            l.removeHandler(handler)
        l.addHandler(file_handler)
        l.setLevel(logging.INFO)

configure_file_logging()

from backend.utils.logger import logger

from mcp.server.fastmcp import FastMCP
from backend.utils.config import get_settings
from backend.mcp.tools import (
    search_schemes as search_schemes_tool,
    get_scheme_details as get_scheme_details_tool,
    check_eligibility as check_eligibility_tool,
)

# Initialize FastMCP Server singleton
settings = get_settings()
mcp = FastMCP(
    name="LabhArth AI",
    instructions="Exposes welfare scheme search, detailed records, and citizen eligibility check tools."
)


# Register MCP tools explicitly using decorators
@mcp.tool(name="search_schemes")
async def search_schemes(
    query: str,
    category: str = None,
    state: str = None,
    limit: int = 10,
) -> dict:
    """
    Search for government welfare schemes using semantic and structured search filters.

    Args:
        query: Natural language query (e.g. 'subsidies for farmers')
        category: Optional category filter (e.g. 'Education', 'Agriculture')
        state: Optional state filter (e.g. 'Maharashtra')
        limit: Maximum results to retrieve (1-50, default 10)
    """
    return await search_schemes_tool(
        query=query,
        category=category,
        state=state,
        limit=limit
    )


@mcp.tool(name="get_scheme_details")
async def get_scheme_details(scheme_id: str) -> dict:
    """
    Retrieve full, comprehensive scheme records from PostgreSQL including benefits, application process, and requirements.

    Args:
        scheme_id: The UUID of the scheme to retrieve details for.
    """
    return await get_scheme_details_tool(scheme_id=scheme_id)


@mcp.tool(name="check_eligibility")
async def check_eligibility(scheme_id: str, user_profile: dict) -> dict:
    """
    Perform rule-based eligibility evaluation matching user profile against scheme rules.

    Args:
        scheme_id: The UUID of the scheme to check.
        user_profile: Dict containing profile fields:
            - age (int): Age in years
            - gender (str): Gender
            - state (str): State of residence
            - category (str): Social category (General/SC/ST/OBC)
            - income_annual (float): Annual income in INR
            - occupation (str): Occupation
            - is_bpl (bool): Below Poverty Line status
            - is_farmer (bool): Farmer status
            - is_student (bool): Student status
    """
    return await check_eligibility_tool(scheme_id=scheme_id, user_profile=user_profile)


class MCPServer:
    """
    MCP Server for LabhArth AI.
    """

    def __init__(self):
        self.settings = settings
        logger.info("MCPServer initialized")

    def register_tools(self) -> None:
        """Register all MCP tools (handled implicitly by decorators)."""
        pass

    async def start(self) -> None:
        """Start the MCP server using stdio transport."""
        logger.info("Starting MCPServer over Stdio transport...")
        mcp.run()


def create_mcp_server() -> MCPServer:
    """Factory function to create and configure an MCP server instance."""
    server = MCPServer()
    return server


if __name__ == "__main__":
    mcp.run()
