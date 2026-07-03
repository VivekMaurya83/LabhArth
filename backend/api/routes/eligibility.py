"""
LabhArth AI — Eligibility Routes
====================================
API endpoints for eligibility checking.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from backend.models.schemas import EligibilityRequest, EligibilityResponse, UserProfile
from backend.security.rate_limiter import rate_limit_dependency
from backend.services import EligibilityService, SchemeService
from backend.api.dependencies import get_eligibility_service, get_scheme_service
from backend.utils.logger import logger

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.post(
    "/check",
    response_model=EligibilityResponse,
    summary="Check Single Scheme Eligibility",
    description="Determine if a user is eligible for a specific government scheme.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def check_single_scheme_eligibility(
    request: EligibilityRequest,
    eligibility_service: EligibilityService = Depends(get_eligibility_service)
) -> EligibilityResponse:
    """Check eligibility for a single specific scheme."""
    logger.info(f"API check_single_scheme_eligibility: scheme={request.scheme_id}")
    try:
        eval_res = await eligibility_service.check_eligibility(
            scheme_id=request.scheme_id,
            user_profile=request.profile.model_dump()
        )
        status_str = eval_res.get("eligibility_status", "Not Eligible")
        is_eligible = (status_str == "Eligible")
        missing_criteria = []
        if eval_res.get("missing_criteria"):
            missing_criteria = [rule.get("reason", rule.get("label", "")) for rule in eval_res["missing_criteria"]]
        
        # Format required documents as a list of strings
        raw_docs = eval_res.get("required_documents") or []
        formatted_docs = []
        for doc in raw_docs:
            if isinstance(doc, dict):
                formatted_docs.append(doc.get("name", ""))
            else:
                formatted_docs.append(str(doc))
        
        return EligibilityResponse(
            scheme_id=UUID(eval_res["scheme_id"]),
            scheme_name=eval_res["scheme_name"],
            is_eligible=is_eligible,
            confidence=eval_res.get("confidence", 0.0),
            reasoning=eval_res.get("reasoning", ""),
            missing_criteria=missing_criteria,
            required_documents=formatted_docs
        )
    except ValueError as val_err:
        logger.warning(f"Eligibility check ValueError: {val_err}")
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        logger.error(f"Error in single scheme check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_model=list[EligibilityResponse],
    summary="Evaluate Profile Eligibility Across Schemes",
    description="Accept a user profile, dynamically retrieve matching schemes, and evaluate eligibility for each.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def evaluate_eligibility(
    profile: UserProfile,
    scheme_service: SchemeService = Depends(get_scheme_service),
    eligibility_service: EligibilityService = Depends(get_eligibility_service)
) -> list[EligibilityResponse]:
    """Evaluate eligibility across multiple matching schemes based on user profile features."""
    logger.info(f"API evaluate_eligibility: age={profile.age}, state={profile.state}, student={profile.is_student}, farmer={profile.is_farmer}")
    
    # 1. Build search query from profile fields
    query_parts = []
    if profile.is_student:
        query_parts.append("student scholarship education")
    if profile.is_farmer:
        query_parts.append("farmer agriculture subsidy")
    if profile.occupation:
        query_parts.append(profile.occupation)
    if profile.category and profile.category.lower() != "general":
        query_parts.append(profile.category)
    if profile.gender:
        query_parts.append(profile.gender)
        
    query = " ".join(query_parts) if query_parts else "welfare schemes"
    
    try:
        # 2. Retrieve candidates filtered by resident state
        matching_schemes = await scheme_service.search_schemes(
            query=query,
            state=profile.state,
            limit=10
        )
        
        if not matching_schemes:
            logger.warning("No matching schemes found for candidate profile")
            raise HTTPException(status_code=404, detail="No matching schemes found for the provided profile criteria.")
            
        # 3. Evaluate eligibility for each candidate
        results = []
        profile_dict = profile.model_dump()
        
        for s in matching_schemes:
            try:
                eval_res = await eligibility_service.check_eligibility(
                    scheme_id=s["id"],
                    user_profile=profile_dict
                )
                
                status_str = eval_res.get("eligibility_status", "Not Eligible")
                is_eligible = (status_str == "Eligible")
                missing_criteria = []
                if eval_res.get("missing_criteria"):
                    missing_criteria = [rule.get("reason", rule.get("label", "")) for rule in eval_res["missing_criteria"]]
                
                # Format required documents as a list of strings
                raw_docs = eval_res.get("required_documents") or []
                formatted_docs = []
                for doc in raw_docs:
                    if isinstance(doc, dict):
                        formatted_docs.append(doc.get("name", ""))
                    else:
                        formatted_docs.append(str(doc))

                results.append(
                    EligibilityResponse(
                        scheme_id=UUID(eval_res["scheme_id"]),
                        scheme_name=eval_res["scheme_name"],
                        is_eligible=is_eligible,
                        confidence=eval_res.get("confidence", 0.0),
                        reasoning=eval_res.get("reasoning", ""),
                        missing_criteria=missing_criteria,
                        required_documents=formatted_docs
                    )
                )
            except Exception as ex:
                logger.error(f"Failed to check eligibility for scheme {s.get('name')} in bulk: {ex}", exc_info=True)
                continue
                
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in evaluate_eligibility: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
