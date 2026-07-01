"""
LabhArth AI — MCP Tool: check_eligibility
============================================
Determine if a user is eligible for a specific scheme.
Exposed as an MCP tool for agent consumption.
"""

import time
from uuid import UUID
from typing import Optional
from backend.services.eligibility_service import EligibilityService
from backend.utils.logger import logger


async def check_eligibility(
    scheme_id: str,
    user_profile: dict,
) -> dict:
    """
    Check if a user is eligible for a government welfare scheme.

    This MCP tool compares the user's profile against the scheme's
    eligibility criteria and returns a detailed assessment.

    Args:
        scheme_id: UUID of the scheme to check eligibility for
        user_profile: Dict containing user profile fields:
            - age (int): Age in years
            - gender (str): Gender
            - state (str): State of residence
            - category (str): Social category (General/SC/ST/OBC)
            - income_annual (float): Annual income in INR
            - occupation (str): Occupation
            - is_bpl (bool): Below Poverty Line status
            - is_farmer (bool): Farmer status
            - is_student (bool): Student status

    Returns:
        Dict containing:
            - scheme_id: The scheme checked
            - eligibility_status: The determination (Eligible, Partially Eligible, Not Eligible)
            - confidence: Confidence score (0.0 to 1.0)
            - reasoning: Explanation of the determination
            - missing_criteria: List of criteria not met or missing
            - required_documents: Documents needed if eligible
    """
    t0 = time.perf_counter()
    logger.info(f"MCP tool check_eligibility: scheme_id={scheme_id}, user_profile_keys={list(user_profile.keys()) if user_profile else None}")

    if not scheme_id or not scheme_id.strip():
        logger.error("Validation error in check_eligibility: scheme_id cannot be empty")
        return {"error": "scheme_id cannot be empty"}

    if user_profile is None or not isinstance(user_profile, dict):
        logger.error("Validation error in check_eligibility: user_profile must be a dictionary")
        return {"error": "user_profile must be a valid dictionary"}

    try:
        # Validate UUID format
        uuid_val = UUID(scheme_id)
    except ValueError as e:
        logger.error(f"Validation error in check_eligibility: invalid UUID format '{scheme_id}'")
        return {"error": f"Invalid scheme_id format. Must be a valid UUID. Error: {str(e)}"}

    try:
        service = EligibilityService()
        result = await service.check_eligibility(uuid_val, user_profile)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(f"MCP check_eligibility succeeded in {duration_ms:.2f}ms for scheme_id={scheme_id}. Result={result.get('eligibility_status')}")
        return result
    except ValueError as val_err:
        logger.warning(f"MCP check_eligibility validation failed: {val_err}")
        return {
            "error": str(val_err),
            "scheme_id": scheme_id
        }
    except Exception as e:
        logger.error(f"MCP check_eligibility failed: {e}", exc_info=True)
        return {
            "error": f"Check eligibility tool failed: {str(e)}",
            "scheme_id": scheme_id
        }
