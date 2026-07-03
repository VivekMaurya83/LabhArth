"""
LabhArth AI — API Dependencies
=================================
Shared FastAPI dependencies used across routes.
"""

from backend.database.connection import get_db_session
from backend.security.auth import verify_api_key
from backend.security.rate_limiter import rate_limit_dependency
from backend.services import RetrievalService, SchemeService, EligibilityService
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from backend.agents import orchestrator_agent

# Thread-safe cached Runner instance for ADK Agents
_runner: Runner = None

def get_orchestrator_runner() -> Runner:
    """Dependency that returns the configured ADK Orchestrator Runner."""
    global _runner
    if _runner is None:
        session_service = InMemorySessionService()
        _runner = Runner(
            agent=orchestrator_agent,
            app_name="LabhArth_AI",
            session_service=session_service,
            auto_create_session=True
        )
    return _runner


def get_retrieval_service() -> RetrievalService:
    """Dependency that returns an instance of RetrievalService."""
    return RetrievalService()


def get_scheme_service() -> SchemeService:
    """Dependency that returns an instance of SchemeService."""
    return SchemeService()


def get_eligibility_service() -> EligibilityService:
    """Dependency that returns an instance of EligibilityService."""
    return EligibilityService()


__all__ = [
    "get_db_session",
    "verify_api_key",
    "rate_limit_dependency",
    "get_retrieval_service",
    "get_scheme_service",
    "get_eligibility_service",
    "get_orchestrator_runner",
]
