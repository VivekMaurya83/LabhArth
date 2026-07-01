"""
LabhArth AI — Scheme Repository
==================================
Data access layer for government schemes.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import Scheme


class SchemeRepository:
    """Repository for scheme CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, scheme_id: UUID) -> Optional[Scheme]:
        """Fetch a single scheme by ID."""
        result = await self.session.execute(
            select(Scheme).where(Scheme.id == scheme_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        category: Optional[str] = None,
        state: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 10,
    ) -> list[Scheme]:
        """Search schemes with optional filters."""
        query = select(Scheme).where(Scheme.status == "active")

        if category:
            query = query.where(Scheme.category == category)
        if state:
            query = query.where(Scheme.state == state)
        if level:
            query = query.where(Scheme.level == level)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_all(self, limit: int = 100) -> list[Scheme]:
        """List all active schemes."""
        result = await self.session.execute(
            select(Scheme).where(Scheme.status == "active").limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, scheme: Scheme) -> Scheme:
        """Create a new scheme record."""
        self.session.add(scheme)
        await self.session.flush()
        return scheme

    async def get_batch_by_ids(self, scheme_ids: list[UUID]) -> list[Scheme]:
        """Fetch multiple schemes by their IDs, preloading their chunks."""
        if not scheme_ids:
            return []
        from sqlalchemy.orm import selectinload
        result = await self.session.execute(
            select(Scheme)
            .options(selectinload(Scheme.chunks))
            .where(Scheme.id.in_(scheme_ids))
        )
        return list(result.scalars().all())

    async def get_chunks_by_scheme_id(self, scheme_id: UUID) -> list:
        """Fetch all chunks associated with a scheme ID."""
        from backend.models.db_models import SchemeChunk
        result = await self.session.execute(
            select(SchemeChunk).where(SchemeChunk.scheme_id == scheme_id)
        )
        return list(result.scalars().all())

    async def search_by_keyword(
        self,
        keyword: str,
        category: Optional[str] = None,
        state: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 10,
    ) -> list[Scheme]:
        """Search schemes by keyword in name or description."""
        query = select(Scheme).where(Scheme.status == "active")
        if keyword:
            keyword_pattern = f"%{keyword}%"
            query = query.where(
                (Scheme.name.ilike(keyword_pattern)) | 
                (Scheme.description.ilike(keyword_pattern))
            )
        if category:
            query = query.where(Scheme.category == category)
        if state:
            from sqlalchemy import or_
            query = query.where(or_(Scheme.state == state, Scheme.state.is_(None)))
        if level:
            query = query.where(Scheme.level == level)
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
