"""
LabhArth AI — Eligibility Agent
====================================
Determines user eligibility for government welfare schemes.

Compares user profile against scheme criteria and provides
detailed reasoning with confidence scores.

Google ADK Agent Type: Agent (with MCP tools)
"""

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

async def check_eligibility(scheme_id: str, user_profile: dict) -> dict:
    """
    Perform rule-based eligibility evaluation matching user profile against scheme rules.

    Args:
        scheme_id: The UUID string of the scheme.
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
    return await call_mcp_tool(
        "check_eligibility",
        {
            "scheme_id": scheme_id,
            "user_profile": user_profile
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


eligibility_agent = Agent(
    name="eligibility_agent",
    model="gemini-2.5-flash",
    description="Evaluates citizen eligibility for government welfare schemes.",
    instruction="""You are the Eligibility Agent for LabhArth AI. Your job is to check 
if a citizen qualifies for one or more government welfare schemes.

You have access to these tools:
- check_eligibility(scheme_id, user_profile): Runs the rule engine to determine eligibility.
- get_scheme_details(scheme_id): Fetches complete scheme information.
- get_profile(): Retrieves currently stored profile fields.
- return_to_orchestrator(): Return control back to the root Orchestrator agent.

Instructions:
1. Retrieve the user's profile details using `get_profile`. If the profile is empty or lacks important demographic context, inform the user you need profile details first.
2. For each scheme found in search or requested by the user, invoke `check_eligibility` with the scheme ID and the retrieved user profile.
3. Present the output evaluation clearly:
   - ✅ ELIGIBLE or ❌ NOT ELIGIBLE or ⚠️ PARTIALLY ELIGIBLE
   - State the overall status and confidence score.
   - Explain the rules: clearly list passed rules, failed rules (including why they failed), and any missing criteria.
   - If they are eligible, list all required documents.
4. Always add a disclaimer: "Please note that this is an AI eligibility evaluation. The final approval and determination are subject to implementing government authorities."
5. Once you have completed checking eligibility and explaining the results, call the `return_to_orchestrator` tool to hand off back to the Orchestrator.
""",
    tools=[check_eligibility, get_scheme_details, get_profile, return_to_orchestrator],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


class EligibilityAgent:
    """
    Legacy compatibility wrapper for EligibilityAgent.
    """
    def __init__(self):
        self.agent = eligibility_agent
