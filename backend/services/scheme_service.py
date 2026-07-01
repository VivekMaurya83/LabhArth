"""
LabhArth AI — Scheme Service
===============================
Business logic for scheme discovery and management.
Orchestrates between database repositories and RAG pipeline.
"""

from typing import Optional
from uuid import UUID

from backend.utils.logger import logger
from backend.services.retrieval_service import RetrievalService
from backend.database.connection import async_session_factory
from backend.database.repositories.scheme_repository import SchemeRepository


class SchemeService:
    """
    Service layer for government scheme operations.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()
        logger.info("SchemeService initialized")

    async def search_schemes(
        self,
        query: str,
        category: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Search for government schemes using semantic + structured search.

        Args:
            query: Natural language search query
            category: Optional category filter
            state: Optional state filter
            limit: Maximum results

        Returns:
            List of matching scheme results
        """
        logger.info(f"Searching schemes: query='{query}', category={category}, state={state}, limit={limit}")
        
        filters = {}
        if category:
            filters["category"] = category
        if state:
            filters["state"] = state

        # Call RAG pipeline through RetrievalService
        result = await self.retrieval_service.retrieve_context(
            query=query,
            filters=filters,
            top_k=limit
        )

        if "error" in result:
            logger.error(f"Search retrieval failed: {result['error']}")
            raise RuntimeError(result["error"])

        # Extract hydrated schemes and map chunks back to them
        schemes_data = result.get("schemes", [])
        chunks_data = result.get("retrieved_chunks", [])

        # Create mapping scheme_id -> list of chunk scores for score tracking
        scores_map = {}
        for chunk in chunks_data:
            s_id = chunk.get("scheme_id")
            score = chunk.get("score", 0.5)
            if s_id not in scores_map:
                scores_map[s_id] = []
            scores_map[s_id].append(score)

        # Average the scores or pick the highest score per scheme
        schemes_out = []
        for s in schemes_data:
            s_id = s.get("id")
            scores = scores_map.get(s_id, [0.5])
            max_score = max(scores)

            schemes_out.append({
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "ministry": s["ministry"],
                "category": s["category"],
                "level": s["level"],
                "state": s["state"],
                "score": float(max_score)
            })

        # Sort by score descending
        schemes_out.sort(key=lambda x: x["score"], reverse=True)
        return schemes_out[:limit]

    async def get_scheme_details(self, scheme_id: UUID) -> Optional[dict]:
        """
        Get full details of a specific scheme.

        Args:
            scheme_id: UUID of the scheme

        Returns:
            Scheme details dict or None if not found
        """
        logger.info(f"Fetching scheme details: {scheme_id}")
        
        # Ensure scheme_id is a UUID object
        if isinstance(scheme_id, str):
            try:
                scheme_id = UUID(scheme_id)
            except ValueError as e:
                logger.error(f"Invalid UUID format for scheme_id: '{scheme_id}'")
                raise ValueError("Invalid scheme_id format. Must be a valid UUID.") from e

        async with async_session_factory() as session:
            repo = SchemeRepository(session)
            scheme = await repo.get_by_id(scheme_id)
            if not scheme:
                logger.warning(f"Scheme not found in DB: {scheme_id}")
                return None

            return {
                "id": str(scheme.id),
                "name": scheme.name,
                "description": scheme.description,
                "ministry": scheme.ministry,
                "category": scheme.category,
                "level": scheme.level,
                "state": scheme.state,
                "eligibility_criteria": scheme.eligibility_criteria,
                "benefits": scheme.benefits,
                "required_documents": scheme.required_documents,
                "application_process": scheme.application_process,
                "official_url": scheme.official_url,
                "status": scheme.status,
                "last_updated": scheme.last_updated.isoformat() if scheme.last_updated else None,
                "created_at": scheme.created_at.isoformat() if scheme.created_at else None
            }
