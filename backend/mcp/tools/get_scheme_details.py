"""
LabhArth AI — MCP Tool: get_scheme_details
=============================================
Retrieve full details of a specific government scheme.
Exposed as an MCP tool for agent consumption.
"""

from backend.utils.logger import logger


async def get_scheme_details(scheme_id: str) -> dict:
    """
    Get comprehensive details of a government welfare scheme.

    This MCP tool fetches all information about a specific scheme
    including eligibility criteria, benefits, documents, and application process.

    Args:
        scheme_id: UUID of the scheme to retrieve

    Returns:
        Dict containing full scheme details:
            - id, name, description
            - ministry, category, level, state
            - eligibility_criteria (structured rules)
            - benefits
            - required_documents (list)
            - application_process
            - official_url
            - status
    """
    logger.info(f"MCP tool get_scheme_details: scheme_id={scheme_id}")
    # TODO: Wire to SchemeService
    return {
        "error": "Scheme not found",
        "scheme_id": scheme_id,
    }
