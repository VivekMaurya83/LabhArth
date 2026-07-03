"""
LabhArth AI — Scheme Routes
===============================
API endpoints for scheme discovery and details.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from backend.models.schemas import (
    SchemeDetailResponse,
    SchemeSearchResponse,
    SchemeResult,
)
from backend.security.rate_limiter import rate_limit_dependency
from backend.services.scheme_service import SchemeService
from backend.api.dependencies import get_scheme_service
from backend.utils.logger import logger

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get(
    "/search",
    response_model=SchemeSearchResponse,
    summary="Search Schemes (GET)",
    description="Search for government welfare schemes using natural language (GET fallback).",
    dependencies=[Depends(rate_limit_dependency)],
)
async def search_schemes(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    category: str = Query(None, description="Filter by category"),
    state: str = Query(None, description="Filter by state"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    scheme_service: SchemeService = Depends(get_scheme_service)
) -> SchemeSearchResponse:
    """Search for government welfare schemes."""
    logger.info(f"API schemes search (GET): query='{query}'")
    try:
        raw_results = await scheme_service.search_schemes(
            query=query,
            category=category,
            state=state,
            limit=limit
        )
        results = [
            SchemeResult(
                id=res["id"],
                name=res["name"],
                description=res["description"],
                category=res["category"],
                level=res["level"],
                state=res["state"],
                relevance_score=res.get("score")
            )
            for res in raw_results
        ]
        return SchemeSearchResponse(results=results, total=len(results), query=query)
    except Exception as e:
        logger.error(f"Error in GET search_schemes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{scheme_id}",
    response_model=SchemeDetailResponse,
    summary="Get Scheme Details",
    description="Retrieve full details of a specific government scheme.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_scheme_details(
    scheme_id: UUID,
    scheme_service: SchemeService = Depends(get_scheme_service)
) -> SchemeDetailResponse:
    """Get full details of a specific scheme."""
    logger.info(f"API get_scheme_details: {scheme_id}")
    try:
        details = await scheme_service.get_scheme_details(scheme_id)
        if not details:
            logger.warning(f"Scheme not found: {scheme_id}")
            raise HTTPException(status_code=404, detail="Scheme not found")
        return SchemeDetailResponse(**details)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_scheme_details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
