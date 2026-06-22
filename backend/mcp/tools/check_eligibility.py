"""
LabhArth AI — MCP Tool: check_eligibility
============================================
Determine if a user is eligible for a specific scheme.
Exposed as an MCP tool for agent consumption.
"""

from typing import Optional

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
            - is_eligible: Boolean eligibility determination
            - confidence: Confidence score (0.0 to 1.0)
            - reasoning: Explanation of the determination
            - missing_criteria: List of criteria not met
            - required_documents: Documents needed if eligible
    """
    logger.info(f"MCP tool check_eligibility: scheme_id={scheme_id}")
    # TODO: Wire to EligibilityService
    return {
        "scheme_id": scheme_id,
        "is_eligible": False,
        "confidence": 0.0,
        "reasoning": "Not yet implemented",
        "missing_criteria": [],
        "required_documents": [],
    }
