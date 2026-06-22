"""
LabhArth AI — Orchestrator Agent
====================================
Root agent that coordinates all sub-agents.

The Orchestrator is the entry point for all user interactions.
It classifies user intent and routes to the appropriate specialized agent.

Google ADK Agent Type: Agent (with sub-agents)
"""

from backend.utils.logger import logger

# Agent configuration — used when ADK is wired in
ORCHESTRATOR_CONFIG = {
    "name": "orchestrator_agent",
    "model": "gemini-2.5-flash",
    "description": "Root orchestrator that routes user queries to specialized agents.",
    "instruction": """You are the LabhArth AI orchestrator. Your job is to help Indian citizens
discover government welfare schemes, check their eligibility, and guide them through applications.

You have access to these specialized sub-agents:
1. **Profile Agent** — Collects and manages user profile information
2. **Scheme Search Agent** — Finds relevant government schemes
3. **Eligibility Agent** — Checks if a user qualifies for a scheme

Routing rules:
- If the user provides personal information (age, income, state, etc.) → Profile Agent
- If the user asks about schemes, searches, or wants recommendations → Scheme Search Agent
- If the user asks about eligibility or qualification → Eligibility Agent
- For general questions, respond directly with helpful information

Always be empathetic, clear, and supportive. Many users may have limited technical literacy.
Respond in simple language. If the user seems to speak Hindi, respond in Hindi.""",
    "sub_agents": [
        "profile_agent",
        "scheme_search_agent",
        "eligibility_agent",
    ],
}


class OrchestratorAgent:
    """
    Orchestrator Agent — entry point for all user conversations.

    TODO: Replace with google.adk.Agent when implementing.
    """

    def __init__(self):
        self.config = ORCHESTRATOR_CONFIG
        logger.info("OrchestratorAgent initialized")

    async def handle_message(self, message: str, session_id: str) -> str:
        """
        Process a user message and route to appropriate sub-agent.

        Args:
            message: User's natural language message
            session_id: Conversation session ID

        Returns:
            Agent response text
        """
        logger.info(f"Orchestrator handling message: session={session_id}")
        # TODO: Implement with Google ADK
        return "LabhArth AI is being set up. Please check back soon!"
