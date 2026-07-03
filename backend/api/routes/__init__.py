"""API Routes package."""

from backend.api.routes.health import router as health_router
from backend.api.routes.schemes import router as schemes_router
from backend.api.routes.eligibility import router as eligibility_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.search import router as search_router

__all__ = ["health_router", "schemes_router", "eligibility_router", "chat_router", "search_router"]
