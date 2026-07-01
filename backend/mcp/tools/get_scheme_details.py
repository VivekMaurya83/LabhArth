"""
LabhArth AI — MCP Tool: get_scheme_details
=============================================
Retrieve full details of a specific government scheme.
Exposed as an MCP tool for agent consumption.
"""

import time
from uuid import UUID
from backend.services.scheme_service import SchemeService
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
    t0 = time.perf_counter()
    logger.info(f"MCP tool get_scheme_details: scheme_id={scheme_id}")

    if not scheme_id or not scheme_id.strip():
        logger.error("Validation error in get_scheme_details: scheme_id cannot be empty")
        return {"error": "scheme_id cannot be empty"}

    try:
        # Validate UUID format
        uuid_val = UUID(scheme_id)
    except ValueError as e:
        logger.error(f"Validation error in get_scheme_details: invalid UUID format '{scheme_id}'")
        return {"error": f"Invalid scheme_id format. Must be a valid UUID. Error: {str(e)}"}

    try:
        service = SchemeService()
        scheme = await service.get_scheme_details(uuid_val)
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if not scheme:
            logger.warning(f"MCP get_scheme_details: scheme not found: {scheme_id}")
            return {
                "error": f"Scheme with ID {scheme_id} not found.",
                "scheme_id": scheme_id
            }

        logger.info(f"MCP get_scheme_details succeeded in {duration_ms:.2f}ms for scheme: {scheme.get('name')}")
        return scheme
    except Exception as e:
        logger.error(f"MCP get_scheme_details failed: {e}", exc_info=True)
        return {
            "error": f"Get scheme details tool failed: {str(e)}",
            "scheme_id": scheme_id
        }
