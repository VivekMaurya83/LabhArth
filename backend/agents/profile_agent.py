"""
LabhArth AI — Profile Agent
================================
Manages user profile collection and maintenance.

Extracts demographic and socioeconomic information from conversation
context to build a profile for eligibility matching.

Google ADK Agent Type: Agent (with function tools)
"""

from backend.utils.logger import logger

PROFILE_AGENT_CONFIG = {
    "name": "profile_agent",
    "model": "gemini-2.5-flash",
    "description": "Collects and manages citizen profile information for eligibility matching.",
    "instruction": """You are the Profile Agent for LabhArth AI. Your job is to collect
and manage user profile information needed for government scheme eligibility checks.

Information to collect (not all required at once):
- Age, Gender
- State, District
- Social Category (General/SC/ST/OBC)
- Annual Income
- Occupation
- Education Level
- BPL (Below Poverty Line) status
- Disability status
- Farmer/Student status

Guidelines:
- Ask one or two questions at a time, not all at once
- Accept approximate values (e.g., "around 2 lakhs")
- Be sensitive when asking about income or social category
- Confirm information before saving
- Explain why each piece of information is needed""",
    "tools": [],  # Function tools will be bound here
}


class ProfileAgent:
    """
    Profile Agent — collects and manages user profiles.

    TODO: Replace with google.adk.Agent when implementing.
    """

    def __init__(self):
        self.config = PROFILE_AGENT_CONFIG
        logger.info("ProfileAgent initialized")

    async def extract_profile(self, message: str, session_id: str) -> dict:
        """
        Extract profile information from a user message.

        Args:
            message: User's message potentially containing profile info
            session_id: Session identifier

        Returns:
            Extracted profile fields
        """
        logger.info(f"ProfileAgent extracting profile: session={session_id}")
        # TODO: Implement with Google ADK + Gemini
        return {}
