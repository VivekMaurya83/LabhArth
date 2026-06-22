"""
LabhArth AI — Scheme Search Agent
=====================================
Discovers relevant government welfare schemes using RAG.

Combines semantic search over scheme embeddings with structured
filtering to find the most relevant schemes for a user's query.

Google ADK Agent Type: Agent (with MCP tools)
"""

from backend.utils.logger import logger

SCHEME_SEARCH_AGENT_CONFIG = {
    "name": "scheme_search_agent",
    "model": "gemini-2.5-flash",
    "description": "Searches and discovers government welfare schemes using semantic search.",
    "instruction": """You are the Scheme Search Agent for LabhArth AI. Your job is to find
relevant government welfare schemes for Indian citizens.

You have access to these tools:
- search_schemes(query, category, state, limit): Search for schemes
- get_scheme_details(scheme_id): Get full scheme details

When searching:
1. Use the user's query and profile context to craft effective searches
2. Apply relevant filters (category, state) when known
3. Present results clearly with scheme name, brief description, and key benefits
4. Offer to show more details for any scheme
5. If few results found, try broader search terms

Always cite the scheme name accurately. Never make up scheme names or details.""",
    "mcp_tools": ["search_schemes", "get_scheme_details"],
}


class SchemeSearchAgent:
    """
    Scheme Search Agent — finds relevant government schemes.

    TODO: Replace with google.adk.Agent when implementing.
    """

    def __init__(self):
        self.config = SCHEME_SEARCH_AGENT_CONFIG
        logger.info("SchemeSearchAgent initialized")

    async def search(self, query: str, context: dict = None) -> dict:
        """
        Search for government schemes based on user query and context.

        Args:
            query: User's search query
            context: Optional context (user profile, filters)

        Returns:
            Search results with scheme summaries
        """
        logger.info(f"SchemeSearchAgent searching: '{query[:50]}'")
        # TODO: Implement with Google ADK + MCP tools
        return {"results": [], "total": 0}
