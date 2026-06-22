"""
LabhArth AI — Scheme Routes
===============================
API endpoints for scheme discovery and details.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.models.schemas import (
    SchemeDetailResponse,
    SchemeSearchRequest,
    SchemeSearchResponse,
)
from backend.security.rate_limiter import rate_limit_dependency
from backend.utils.logger import logger

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get(
    "/search",
    response_model=SchemeSearchResponse,
    summary="Search Schemes",
    description="Search for government welfare schemes using natural language.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def search_schemes(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    category: str = Query(None, description="Filter by category"),
    state: str = Query(None, description="Filter by state"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
) -> SchemeSearchResponse:
    """Search for government welfare schemes."""
    logger.info(f"API search_schemes: query='{query}'")
    # TODO: Wire to SchemeService
    return SchemeSearchResponse(results=[], total=0, query=query)


@router.get(
    "/{scheme_id}",
    response_model=SchemeDetailResponse,
    summary="Get Scheme Details",
    description="Retrieve full details of a specific government scheme.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_scheme_details(scheme_id: UUID) -> SchemeDetailResponse:
    """Get full details of a specific scheme."""
    logger.info(f"API get_scheme_details: {scheme_id}")
    # TODO: Wire to SchemeService
    return SchemeDetailResponse(
        id=scheme_id,
        name="Placeholder Scheme",
        description="This endpoint is not yet implemented.",
    )
