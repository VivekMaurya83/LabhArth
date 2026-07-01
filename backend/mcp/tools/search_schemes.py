"""
LabhArth AI — MCP Tool: search_schemes
=========================================
Search for government welfare schemes using semantic + structured search.
Exposed as an MCP tool for agent consumption.
"""

import time
from typing import Optional
from backend.services.scheme_service import SchemeService
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
    t0 = time.perf_counter()
    logger.info(f"MCP tool search_schemes: query='{query}', category={category}, state={state}, limit={limit}")
    
    if not query or not query.strip():
        logger.error("Validation error in search_schemes: query cannot be empty")
        return {
            "error": "Query cannot be empty",
            "query": query,
            "results": [],
            "total": 0
        }

    try:
        service = SchemeService()
        results = await service.search_schemes(
            query=query,
            category=category,
            state=state,
            limit=limit
        )
        duration_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(f"MCP search_schemes succeeded in {duration_ms:.2f}ms. Found {len(results)} results.")
        return {
            "results": results,
            "total": len(results),
            "query": query,
        }
    except Exception as e:
        logger.error(f"MCP search_schemes failed: {e}", exc_info=True)
        return {
            "error": f"Search schemes tool failed: {str(e)}",
            "query": query,
            "results": [],
            "total": 0
        }
