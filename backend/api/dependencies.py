"""
LabhArth AI — API Dependencies
=================================
Shared FastAPI dependencies used across routes.
"""

from backend.database.connection import get_db_session
from backend.security.auth import verify_api_key
from backend.security.rate_limiter import rate_limit_dependency

__all__ = ["get_db_session", "verify_api_key", "rate_limit_dependency"]
