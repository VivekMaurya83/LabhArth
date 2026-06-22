"""
LabhArth AI — Rate Limiter
=============================
Simple in-memory rate limiter using token bucket algorithm.
For production, replace with Redis-backed solution.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from backend.utils.config import get_settings


class RateLimiter:
    """In-memory token bucket rate limiter."""

    def __init__(self):
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup(self, client_id: str, window: int) -> None:
        """Remove expired timestamps."""
        now = time.time()
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if now - ts < window
        ]

    def check(self, client_id: str) -> bool:
        """
        Check if the client is within the rate limit.

        Returns True if allowed, raises HTTPException if rate-limited.
        """
        settings = get_settings()
        window = 60  # 1 minute window
        max_requests = settings.rate_limit_per_minute

        self._cleanup(client_id, window)

        if len(self.requests[client_id]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {max_requests} requests per minute.",
            )

        self.requests[client_id].append(time.time())
        return True


# Singleton instance
rate_limiter = RateLimiter()


async def rate_limit_dependency(request: Request) -> None:
    """FastAPI dependency for rate limiting by client IP."""
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)
