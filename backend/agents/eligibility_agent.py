"""
LabhArth AI — Eligibility Agent
====================================
Determines user eligibility for government welfare schemes.

Compares user profile against scheme criteria and provides
detailed reasoning with confidence scores.

Google ADK Agent Type: Agent (with MCP tools)
"""

from backend.utils.logger import logger

ELIGIBILITY_AGENT_CONFIG = {
    "name": "eligibility_agent",
    "model": "gemini-2.5-flash",
    "description": "Checks citizen eligibility for government welfare schemes.",
    "instruction": """You are the Eligibility Agent for LabhArth AI. Your job is to determine
if a citizen qualifies for a specific government welfare scheme.

You have access to:
- check_eligibility(scheme_id, user_profile): Check eligibility for a scheme

When checking eligibility:
1. Ensure you have the user's profile information (request via Profile Agent if missing)
2. Use the check_eligibility tool with the user's profile
3. Present results clearly:
   - ✅ ELIGIBLE or ❌ NOT ELIGIBLE
   - Confidence level
   - Clear reasoning
   - Missing criteria (if not eligible)
   - Required documents (if eligible)
4. Suggest similar schemes if not eligible

Be accurate and honest. Never guarantee eligibility — always note that
final determination is made by the implementing authority.""",
    "mcp_tools": ["check_eligibility"],
}


class EligibilityAgent:
    """
    Eligibility Agent — checks scheme eligibility.

    TODO: Replace with google.adk.Agent when implementing.
    """

    def __init__(self):
        self.config = ELIGIBILITY_AGENT_CONFIG
        logger.info("EligibilityAgent initialized")

    async def check(self, scheme_id: str, user_profile: dict) -> dict:
        """
        Check if a user is eligible for a specific scheme.

        Args:
            scheme_id: UUID of the target scheme
            user_profile: User profile data

        Returns:
            Eligibility assessment with reasoning
        """
        logger.info(f"EligibilityAgent checking: scheme={scheme_id}")
        # TODO: Implement with Google ADK + MCP tools
        return {
            "is_eligible": False,
            "confidence": 0.0,
            "reasoning": "Not yet implemented",
        }
