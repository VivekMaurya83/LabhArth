"""
LabhArth AI — API Package
============================
FastAPI route handlers, middleware, and dependencies.
"""

from backend.api.routes import (
    chat_router,
    eligibility_router,
    health_router,
    schemes_router,
)

__all__ = ["health_router", "schemes_router", "eligibility_router", "chat_router"]
