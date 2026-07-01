"""
LabhArth AI — Retrieval Service
=================================
Business logic for retrieval operations. Handles DB session lifecycle,
error checking, and logging of performance telemetry.
"""

from typing import Any, Dict, Optional

from backend.rag.pipeline import RAGPipeline
from backend.database.connection import async_session_factory
from backend.utils.logger import logger


class RetrievalService:
    """
    Service layer encapsulating RAG pipeline operations.
    """

    def __init__(self):
        self.pipeline = RAGPipeline()
        logger.info("RetrievalService initialized")

    async def retrieve_context(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Coordinates full RAG retrieval pipeline with DB session management.

        Args:
            query: User's natural language query
            filters: Optional filters (category, state, level, ministry)
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score filter

        Returns:
            Dict containing retrieved contexts, schemes, and execution metrics.
        """
        if not query or not query.strip():
            logger.warning("Empty query received in retrieval service")
            return {
                "question": query,
                "context_text": "",
                "retrieved_chunks": [],
                "schemes": [],
                "error": "Query cannot be empty",
                "metrics": {
                    "embedding_latency_ms": 0.0,
                    "qdrant_search_latency_ms": 0.0,
                    "postgres_hydration_latency_ms": 0.0,
                    "total_pipeline_latency_ms": 0.0
                }
            }

        try:
            async with async_session_factory() as session:
                logger.info(f"Executing retrieval for query='{query[:50]}'")
                result = await self.pipeline.query(
                    question=query,
                    session=session,
                    filters=filters,
                    top_k=top_k,
                    score_threshold=score_threshold
                )
                
                # Log execution latencies
                metrics = result.get("metrics", {})
                logger.info(
                    f"Retrieval success: {len(result.get('retrieved_chunks', []))} chunks found. "
                    f"Latencies: embed={metrics.get('embedding_latency_ms', 0):.2f}ms, "
                    f"qdrant={metrics.get('qdrant_search_latency_ms', 0):.2f}ms, "
                    f"postgres={metrics.get('postgres_hydration_latency_ms', 0):.2f}ms, "
                    f"total={metrics.get('total_pipeline_latency_ms', 0):.2f}ms"
                )
                return result

        except Exception as e:
            logger.error(f"Error during RAG retrieval operation: {e}", exc_info=True)
            return {
                "question": query,
                "context_text": "",
                "retrieved_chunks": [],
                "schemes": [],
                "error": f"Failed to retrieve context: {str(e)}",
                "metrics": {
                    "embedding_latency_ms": 0.0,
                    "qdrant_search_latency_ms": 0.0,
                    "postgres_hydration_latency_ms": 0.0,
                    "total_pipeline_latency_ms": 0.0
                }
            }
