"""
LabhArth AI — Health Check Route
===================================
"""

from fastapi import APIRouter

from backend.models.schemas import HealthResponse
from backend.utils.config import get_settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy.",
)
async def health_check() -> HealthResponse:
    """Return the current health status of the API."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
    )
