"""
LabhArth AI — Orchestrator Agent
====================================
Root agent that coordinates all sub-agents.

The Orchestrator is the entry point for all user interactions.
It classifies user intent and routes to the appropriate specialized agent.

Google ADK Agent Type: Agent (with sub-agents)
"""

from google.adk import Agent
from backend.agents.profile_agent import profile_agent
from backend.agents.scheme_search_agent import scheme_search_agent
from backend.agents.eligibility_agent import eligibility_agent
from backend.agents.callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_tool_callback,
    after_tool_callback,
    route_to_agent,
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gemini-3.1-flash-lite",
    description="Root orchestrator that routes user queries to specialized agents.",
    instruction="""You are the LabhArth AI Orchestrator Agent. Your job is to guide Indian citizens
through government welfare scheme discovery and eligibility evaluations.

You coordinate three sub-agents:
1. **profile_agent** — extracts and stores user profile information (such as age, state, category, income, etc.) in the session state.
2. **scheme_search_agent** — searches for relevant welfare schemes using the RAG index.
3. **eligibility_agent** — runs the rule engine to determine if the user qualifies for the retrieved schemes.

You have access to:
- route_to_agent(agent_name): Transfers execution control to a target sub-agent.

Orchestration Workflow:
- If the user provides personal demographic details (e.g. "I am a 20-year-old student from Maharashtra...") or answers a question about themselves → Call `route_to_agent` with 'profile_agent' to extract and update the profile in the session state.
- Once the profile is updated or if the user asks for scheme recommendations → Call `route_to_agent` with 'scheme_search_agent' to run the similarity search queries.
- Once matching schemes are found, or if the user asks if they qualify for a scheme → Call `route_to_agent` with 'eligibility_agent' to evaluate eligibility and explain results.
- When a sub-agent completes its task and hands control back to you, DO NOT duplicate or repeat the lists of schemes, eligibility details, or documents that the sub-agent has already printed. Simply append a clean, friendly next-step suggestion or guide them on how to proceed. Only synthesize a full response if the sub-agents did not output any details yet.
""",
    tools=[route_to_agent],
    sub_agents=[
        profile_agent,
        scheme_search_agent,
        eligibility_agent,
    ],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


class OrchestratorAgent:
    """
    Legacy compatibility wrapper for OrchestratorAgent.
    """
    def __init__(self):
        self.agent = orchestrator_agent
