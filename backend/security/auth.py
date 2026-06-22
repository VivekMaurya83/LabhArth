"""
LabhArth AI — Authentication
===============================
API key validation and security middleware.
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from backend.utils.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Validate the API key from the request header.

    In development mode, authentication is optional.
    In production, a valid API key is required.

    Returns:
        The validated API key string.

    Raises:
        HTTPException: If the API key is missing or invalid in production.
    """
    settings = get_settings()

    # In development, allow requests without API key
    if not settings.is_production and not api_key:
        return "dev-mode"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
        )

    if api_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key
