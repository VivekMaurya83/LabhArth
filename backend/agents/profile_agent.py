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
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    age: Optional[int] = Field(None, description="Age in years")
    gender: Optional[str] = Field(None, description="Gender (e.g., Male, Female)")
    state: Optional[str] = Field(None, description="State of residence (e.g., Maharashtra, Karnataka, Gujarat)")
    category: Optional[str] = Field(None, description="Social category (General/SC/ST/OBC)")
    income_annual: Optional[float] = Field(None, description="Annual family income in INR")
    occupation: Optional[str] = Field(None, description="Occupation of the citizen")
    is_bpl: Optional[bool] = Field(None, description="True if below poverty line")
    is_farmer: Optional[bool] = Field(None, description="True if a farmer")
    is_student: Optional[bool] = Field(None, description="True if a student")

def save_profile(
    tool_context: ToolContext,
    profile: UserProfile
) -> str:
    """
    Save or update the user's profile details in the persistent session state.

    Args:
        tool_context: The execution context injected by ADK.
        profile: The user profile object containing citizen demographic details.
    """
    if "profile" not in tool_context.session.state:
        tool_context.session.state["profile"] = {}
    
    profile_dict = profile.model_dump(exclude_none=True)
    tool_context.session.state["profile"].update(profile_dict)
    return f"Profile updated successfully. Current profile: {tool_context.session.state['profile']}"

def get_profile(tool_context: ToolContext) -> dict:
    """
    Retrieve the current user profile fields stored in the conversation session state.
    """
    return tool_context.session.state.get("profile", {})


profile_agent = Agent(
    name="profile_agent",
    model="gemini-3.1-flash-lite",
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
4. Present a summary of the saved profile, and then call the `return_to_orchestrator` tool to hand control back. Do NOT output any system or transition comments like 'I am returning control' or 'Handoff initiated'. Just show the profile facts and run the tool.
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
