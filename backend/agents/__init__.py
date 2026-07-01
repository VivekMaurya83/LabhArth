"""
LabhArth AI — Agents Package
===============================
Google ADK agent definitions for the multi-agent architecture.

Agent hierarchy:
  Orchestrator Agent (root)
  ├── Profile Agent
  ├── Scheme Search Agent
  └── Eligibility Agent
"""

from backend.agents.orchestrator_agent import OrchestratorAgent, orchestrator_agent
from backend.agents.profile_agent import ProfileAgent, profile_agent
from backend.agents.scheme_search_agent import SchemeSearchAgent, scheme_search_agent
from backend.agents.eligibility_agent import EligibilityAgent, eligibility_agent

__all__ = [
    "OrchestratorAgent",
    "ProfileAgent",
    "SchemeSearchAgent",
    "EligibilityAgent",
    "orchestrator_agent",
    "profile_agent",
    "scheme_search_agent",
    "eligibility_agent",
]
