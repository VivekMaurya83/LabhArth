"""
LabhArth AI — Scheme Search Agent
=====================================
Discovers relevant government welfare schemes using RAG.

Combines semantic search over scheme embeddings with structured
filtering to find the most relevant schemes for a user's query.

Google ADK Agent Type: Agent (with MCP tools)
"""

from typing import Optional
from google.adk import Agent
from google.adk.tools import ToolContext
from backend.agents.callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_tool_callback,
    after_tool_callback,
    return_to_orchestrator,
)
from backend.agents.mcp_client_helper import call_mcp_tool

async def search_schemes(
    query: str,
    category: str = "",
    state: str = "",
    limit: int = 5
) -> dict:
    """
    Search for government welfare schemes using semantic and structured search filters.

    Args:
        query: Natural language query (e.g. 'subsidies for farmers')
        category: Optional category filter (e.g. 'Education', 'Agriculture')
        state: Optional state filter (e.g. 'Maharashtra')
        limit: Maximum results to retrieve (default 5)
    """
    return await call_mcp_tool(
        "search_schemes",
        {
            "query": query,
            "category": category if category != "" else None,
            "state": state if state != "" else None,
            "limit": limit
        }
    )

async def get_scheme_details(scheme_id: str) -> dict:
    """
    Retrieve full, comprehensive scheme records from PostgreSQL by UUID.

    Args:
        scheme_id: The UUID string of the scheme.
    """
    return await call_mcp_tool(
        "get_scheme_details",
        {
            "scheme_id": scheme_id
        }
    )

def get_profile(tool_context: ToolContext) -> dict:
    """
    Retrieve the current user profile fields stored in the conversation session state.
    """
    return tool_context.session.state.get("profile", {})


scheme_search_agent = Agent(
    name="scheme_search_agent",
    model="gemini-2.5-flash",
    description="Searches and discovers government welfare schemes using semantic search.",
    instruction="""You are the Scheme Search Agent for LabhArth AI. Your job is to find 
relevant government welfare schemes for Indian citizens.

You have access to these tools:
- search_schemes(query, category, state, limit): Search for welfare schemes
- get_scheme_details(scheme_id): Get complete scheme details
- get_profile(): Retrieve currently stored user profile fields
- return_to_orchestrator(): Return control back to the root Orchestrator agent.

Instructions:
1. First, retrieve the user's profile details using `get_profile` to check if there are any specific profile attributes available (e.g., state, category, occupation).
2. Run search queries using the `search_schemes` tool. Make sure to apply state and category filters if they are present in the user profile (e.g. state='Maharashtra' if the profile says Maharashtra).
3. If search_schemes returns matching schemes, present them to the user. For each matching scheme:
   - Print its Name, ID (UUID), and a brief description/benefit.
4. If the user asks for detailed information about a specific scheme, call `get_scheme_details` with the scheme ID and summarize the benefits, application process, and requirements.
5. Once you have shown the matching schemes or details, call the `return_to_orchestrator` tool to hand off back to the Orchestrator.
""",
    tools=[search_schemes, get_scheme_details, get_profile, return_to_orchestrator],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


class SchemeSearchAgent:
    """
    Legacy compatibility wrapper for SchemeSearchAgent.
    """
    def __init__(self):
        self.agent = scheme_search_agent
