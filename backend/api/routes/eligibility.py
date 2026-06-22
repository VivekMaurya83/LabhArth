"""
LabhArth AI — Eligibility Routes
====================================
API endpoints for eligibility checking.
"""

from fastapi import APIRouter, Depends

from backend.models.schemas import EligibilityRequest, EligibilityResponse
from backend.security.rate_limiter import rate_limit_dependency
from backend.utils.logger import logger

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.post(
    "/check",
    response_model=EligibilityResponse,
    summary="Check Eligibility",
    description="Determine if a user is eligible for a specific government scheme.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def check_eligibility(request: EligibilityRequest) -> EligibilityResponse:
    """Check eligibility for a government scheme."""
    logger.info(f"API check_eligibility: scheme={request.scheme_id}")
    # TODO: Wire to EligibilityService
    return EligibilityResponse(
        scheme_id=request.scheme_id,
        scheme_name="Placeholder Scheme",
        is_eligible=False,
        confidence=0.0,
        reasoning="Eligibility checking is not yet implemented.",
        missing_criteria=[],
        required_documents=[],
    )
