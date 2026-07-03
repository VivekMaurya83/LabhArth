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
from backend.utils.sanitizer import clean_text, sanitize_value, sanitize_eligibility


class SchemeService:
    """
    Service layer for government scheme operations.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self._details_cache = {}
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
        
        # If query is empty, bypass RAG and perform a direct database search using category and state
        if not query or not query.strip():
            logger.info("Empty query received. Bypassing RAG and performing direct SQL structured filtering.")
            from backend.database.connection import async_session_factory
            from backend.database.repositories.scheme_repository import SchemeRepository
            
            async with async_session_factory() as session:
                repo = SchemeRepository(session)
                schemes = await repo.search_by_keyword(
                    keyword="",
                    category=category,
                    state=state,
                    limit=limit
                )
                
                return [
                    {
                        "id": s.id,
                        "name": clean_text(s.name),
                        "description": clean_text(s.description, is_description=True),
                        "ministry": clean_text(s.ministry),
                        "category": s.category,
                        "level": s.level,
                        "state": s.state,
                        "eligibility_criteria": sanitize_eligibility(s.eligibility_criteria),
                        "benefits": clean_text(s.benefits),
                        "required_documents": sanitize_value(s.required_documents),
                        "application_process": clean_text(s.application_process),
                        "official_url": s.official_url,
                        "score": 1.0
                    }
                    for s in schemes
                ]

        filters = {}
        if category:
            filters["category"] = category
        if state:
            filters["state"] = state

        # Call RAG pipeline through RetrievalService with graceful SQL database keyword fallback
        try:
            result = await self.retrieval_service.retrieve_context(
                query=query,
                filters=filters,
                top_k=limit
            )
            if "error" in result:
                raise RuntimeError(result["error"])
            
            # Extract hydrated schemes and map chunks back to them
            schemes_data = result.get("schemes", [])

            # Fallback to SQL keyword search if semantic search yields 0 matches
            if not schemes_data and query.strip():
                logger.info("Qdrant returned 0 results. Falling back to SQL keyword search.")
                async with async_session_factory() as session:
                    repo = SchemeRepository(session)
                    schemes = await repo.search_by_keyword(
                        keyword=query,
                        category=category,
                        state=state,
                        limit=limit
                    )
                return [
                    {
                        "id": str(s.id),
                        "name": clean_text(s.name),
                        "description": clean_text(s.description, is_description=True),
                        "ministry": clean_text(s.ministry),
                        "category": s.category,
                        "level": s.level,
                        "state": s.state,
                        "score": 0.5
                    }
                    for s in schemes
                ]

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
                    "name": clean_text(s["name"]),
                    "description": clean_text(s["description"], is_description=True),
                    "ministry": clean_text(s["ministry"]),
                    "category": s["category"],
                    "level": s["level"],
                    "state": s["state"],
                    "score": float(max_score)
                })

            # Sort by score descending
            schemes_out.sort(key=lambda x: x["score"], reverse=True)
            return schemes_out[:limit]

        except Exception as exc:
            logger.warning(f"⚠️ RAG retrieval failed (falling back to database keyword search): {exc}")
            
            # Fallback path: query SQL database repository directly using search_by_keyword!
            async with async_session_factory() as session:
                repo = SchemeRepository(session)
                schemes = await repo.search_by_keyword(
                    keyword=query,
                    category=category,
                    state=state,
                    limit=limit
                )
            
            return [
                {
                    "id": str(s.id),
                    "name": clean_text(s.name),
                    "description": clean_text(s.description, is_description=True),
                    "ministry": clean_text(s.ministry),
                    "category": s.category,
                    "level": s.level,
                    "state": s.state,
                    "score": 0.5
                }
                for s in schemes
            ]

    async def get_scheme_details(self, scheme_id: UUID) -> Optional[dict]:
        """
        Get full details of a specific scheme.

        Args:
            scheme_id: UUID of the scheme

        Returns:
            Scheme details dict or None if not found
        """
        logger.info(f"Fetching scheme details: {scheme_id}")
        
        # Ensure scheme_id is a UUID object or validate string
        str_id = str(scheme_id)
        if str_id in self._details_cache:
            logger.info(f"Cache hit for scheme details: {str_id}")
            return self._details_cache[str_id]

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

            details = {
                "id": str(scheme.id),
                "name": clean_text(scheme.name),
                "description": clean_text(scheme.description, is_description=True),
                "ministry": clean_text(scheme.ministry),
                "category": scheme.category,
                "level": scheme.level,
                "state": scheme.state,
                "eligibility_criteria": sanitize_eligibility(scheme.eligibility_criteria),
                "benefits": clean_text(scheme.benefits),
                "required_documents": sanitize_value(scheme.required_documents),
                "application_process": clean_text(scheme.application_process),
                "official_url": scheme.official_url,
                "status": scheme.status,
                "last_updated": scheme.last_updated.isoformat() if scheme.last_updated else None,
                "created_at": scheme.created_at.isoformat() if scheme.created_at else None
            }
            
            # Cache the result
            self._details_cache[str_id] = details
            return details
