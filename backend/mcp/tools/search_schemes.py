"""
LabhArth AI — MCP Tool: search_schemes
=========================================
Search for government welfare schemes using semantic + structured search.
Exposed as an MCP tool for agent consumption.
"""

from typing import Optional

from backend.utils.logger import logger


async def search_schemes(
    query: str,
    category: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Search for government welfare schemes.

    This MCP tool combines vector similarity search (Qdrant) with
    structured filtering (PostgreSQL) to find relevant schemes.

    Args:
        query: Natural language search query (e.g., "farming subsidies in UP")
        category: Filter by scheme category (e.g., "agriculture", "education")
        state: Filter by state (e.g., "Uttar Pradesh")
        limit: Maximum number of results to return (1-50)

    Returns:
        Dict containing:
            - results: List of matching schemes with id, name, description, score
            - total: Total number of matches
            - query: Original search query
    """
    logger.info(f"MCP tool search_schemes: query='{query}', category={category}, state={state}")
    # TODO: Wire to SchemeService
    return {
        "results": [],
        "total": 0,
        "query": query,
    }
