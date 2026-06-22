"""
LabhArth AI — User Repository
================================
Data access layer for user profiles.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import UserProfile


class UserRepository:
    """Repository for user profile CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_session_id(self, session_id: str) -> Optional[UserProfile]:
        """Fetch a user profile by session ID."""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, session_id: str, profile_data: dict
    ) -> UserProfile:
        """Create or update a user profile."""
        existing = await self.get_by_session_id(session_id)

        if existing:
            for key, value in profile_data.items():
                if value is not None and hasattr(existing, key):
                    setattr(existing, key, value)
            await self.session.flush()
            return existing

        profile = UserProfile(session_id=session_id, **profile_data)
        self.session.add(profile)
        await self.session.flush()
        return profile
