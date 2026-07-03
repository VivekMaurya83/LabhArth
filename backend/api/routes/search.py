"""
LabhArth AI — Search Routes
==============================
API endpoints for semantic search over government schemes.
"""

from fastapi import APIRouter, Depends

from backend.models.schemas import SchemeSearchRequest, SchemeSearchResponse, SchemeResult
from backend.security.rate_limiter import rate_limit_dependency
from backend.services.scheme_service import SchemeService
from backend.api.dependencies import get_scheme_service
from backend.utils.logger import logger

router = APIRouter(tags=["Search"])


@router.post(
    "/search",
    response_model=SchemeSearchResponse,
    summary="Semantic Scheme Search",
    description="Perform semantic search over government welfare schemes based on user query and optional category/state filters.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def search_schemes(
    request: SchemeSearchRequest,
    scheme_service: SchemeService = Depends(get_scheme_service)
) -> SchemeSearchResponse:
    """Perform semantic search and return ranked schemes."""
    logger.info(f"API search: query='{request.query}', category={request.category}, state={request.state}")
    
    try:
        raw_results = await scheme_service.search_schemes(
            query=request.query,
            category=request.category,
            state=request.state,
            limit=request.limit
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
        
        return SchemeSearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}", exc_info=True)
        raise
