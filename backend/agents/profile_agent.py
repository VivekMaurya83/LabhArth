"""
LabhArth AI — Profile Agent
================================
Manages user profile collection and maintenance.

Extracts demographic and socioeconomic information from conversation
context to build a profile for eligibility matching.

Google ADK Agent Type: Agent (with function tools)
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

from typing import Optional

def save_profile(
    tool_context: ToolContext,
    age: int = -1,
    gender: str = "",
    state: str = "",
    category: str = "",
    income_annual: float = -1.0,
    occupation: str = "",
    is_bpl: bool = False,
    is_farmer: bool = False,
    is_student: bool = False,
    annual_income: float = -1.0
) -> str:
    """
    Save or update the user's profile details in the persistent session state.

    Args:
        tool_context: The execution context injected by ADK.
        age: Age of the citizen in years (integer)
        gender: Gender of the citizen (e.g. 'Male', 'Female')
        state: State of residence (e.g. 'Maharashtra', 'Gujarat', 'Karnataka')
        category: Social category (e.g. 'General', 'SC', 'ST', 'OBC')
        income_annual: Annual income of the family in INR (float)
        occupation: Occupation of the citizen
        is_bpl: Whether the citizen is below poverty line (boolean)
        is_farmer: Whether the citizen is a farmer (boolean)
        is_student: Whether the citizen is a student (boolean)
        annual_income: Alias for income_annual (annual family income in INR)
    """
    if "profile" not in tool_context.session.state:
        tool_context.session.state["profile"] = {}
    
    updates = {}
    if age != -1: updates["age"] = int(age)
    if gender != "": updates["gender"] = gender
    if state != "": updates["state"] = state
    if category != "": updates["category"] = category
    
    income = income_annual if income_annual != -1.0 else annual_income
    if income != -1.0: updates["income_annual"] = float(income)
    
    if occupation != "": updates["occupation"] = occupation
    if is_bpl is not False: updates["is_bpl"] = bool(is_bpl)
    if is_farmer is not False: updates["is_farmer"] = bool(is_farmer)
    if is_student is not False: updates["is_student"] = bool(is_student)
    
    tool_context.session.state["profile"].update(updates)
    return f"Profile updated successfully. Current profile: {tool_context.session.state['profile']}"

def get_profile(tool_context: ToolContext) -> dict:
    """
    Retrieve the current user profile fields stored in the conversation session state.
    """
    return tool_context.session.state.get("profile", {})


profile_agent = Agent(
    name="profile_agent",
    model="gemini-2.5-flash",
    description="Extracts and manages citizen profile information for eligibility checks.",
    instruction="""You are the Profile Agent for LabhArth AI. Your job is to extract 
and manage user profile information needed for government scheme eligibility checks.

You have access to these tools:
- save_profile(profile): Save or update profile fields.
- get_profile(): Retrieve currently stored profile fields.
- return_to_orchestrator(): Return control back to the root Orchestrator agent.

Instructions:
1. Examine the user's input and conversation history to extract demographic/socioeconomic parameters.
2. Call the `save_profile` tool immediately with whatever fields are extracted (e.g., state, occupation, is_student, is_farmer).
3. Do not halt or ask the user for missing details; proceed immediately with whatever information is available.
4. Present a summary of the saved profile, and then call the `return_to_orchestrator` tool to hand control back to the Orchestrator.
""",
    tools=[save_profile, get_profile, return_to_orchestrator],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


class ProfileAgent:
    """
    Legacy compatibility wrapper for ProfileAgent.
    """
    def __init__(self):
        self.agent = profile_agent
