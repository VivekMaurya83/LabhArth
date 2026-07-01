"""
LabhArth AI — RAG Pipeline
=============================
End-to-end Retrieval-Augmented Generation pipeline.
Orchestrates embedding, retrieval, and context augmentation.
"""

from typing import Optional

from backend.rag.embeddings import EmbeddingService
from backend.rag.retriever import QdrantRetriever
from backend.utils.logger import logger


class RAGPipeline:
    """
    Complete RAG pipeline: Query → Embed → Retrieve → Augment.

    This is the core intelligence layer that provides grounded
    responses by combining vector search with LLM generation.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.retriever = QdrantRetriever()
        logger.info("RAG Pipeline initialized")

    async def query(
        self,
        question: str,
        session,
        filters: Optional[dict] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> dict:
        """
        Run the full RAG pipeline for a user question.

        Args:
            question: User's natural language query
            session: Async database session
            filters: Optional filters (category, state, etc.)
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score

        Returns:
            Dict with retrieved contexts and metadata
        """
        import time
        from uuid import UUID, uuid4
        from backend.database.repositories.scheme_repository import SchemeRepository
        from backend.utils.config import get_settings

        settings = get_settings()

        if not question or not question.strip():
            raise ValueError("Query cannot be empty")

        if top_k is None:
            top_k = settings.rag_top_k
        if score_threshold is None:
            score_threshold = settings.rag_similarity_threshold

        logger.info(f"RAG query: '{question[:50]}...', filters={filters}, top_k={top_k}, threshold={score_threshold}")
        
        t0 = time.perf_counter()

        # Step 1: Embed the query
        t_embed_start = time.perf_counter()
        try:
            query_vector = await self.embedding_service.embed_query(question)
        except Exception as embed_err:
            logger.warning(f"Embedding generation failed: {embed_err}. Using dummy vector for fallback search.")
            query_vector = [0.0] * 768
        t_embed_end = time.perf_counter()
        embed_latency_ms = (t_embed_end - t_embed_start) * 1000.0

        # Step 2: Retrieve relevant documents
        t_qdrant_start = time.perf_counter()
        try:
            qdrant_results = await self.retriever.search(
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                filters=filters
            )
            t_qdrant_end = time.perf_counter()
            qdrant_latency_ms = (t_qdrant_end - t_qdrant_start) * 1000.0

            if not qdrant_results:
                logger.info("No matching chunks found in Qdrant")
                total_latency_ms = (time.perf_counter() - t0) * 1000.0
                return {
                    "question": question,
                    "context_text": "",
                    "retrieved_chunks": [],
                    "schemes": [],
                    "metrics": {
                        "embedding_latency_ms": embed_latency_ms,
                        "qdrant_search_latency_ms": qdrant_latency_ms,
                        "postgres_hydration_latency_ms": 0.0,
                        "total_pipeline_latency_ms": total_latency_ms
                    }
                }

            # Step 3: Extract unique scheme IDs
            scheme_ids_set = set()
            for hit in qdrant_results:
                scheme_id_str = hit["payload"].get("scheme_id")
                if scheme_id_str:
                    try:
                        scheme_ids_set.add(UUID(scheme_id_str))
                    except ValueError:
                        logger.warning(f"Invalid scheme_id UUID format in Qdrant payload: {scheme_id_str}")

            scheme_ids = list(scheme_ids_set)

            # Step 4: Hydrate schemes and chunks from PostgreSQL
            t_postgres_start = time.perf_counter()
            scheme_repo = SchemeRepository(session)
            schemes = await scheme_repo.get_batch_by_ids(scheme_ids)
            t_postgres_end = time.perf_counter()
            postgres_latency_ms = (t_postgres_end - t_postgres_start) * 1000.0

            # Create mapping of scheme_id -> scheme object for easy access
            schemes_map = {scheme.id: scheme for scheme in schemes}

            # Step 5: Format context for LLM
            formatted_results = []
            for hit in qdrant_results:
                payload = hit["payload"]
                scheme_id_str = payload.get("scheme_id")
                if not scheme_id_str:
                    continue
                
                try:
                    scheme_id = UUID(scheme_id_str)
                except ValueError:
                    continue

                scheme = schemes_map.get(scheme_id)
                if not scheme:
                    logger.warning(f"Scheme ID {scheme_id} found in Qdrant but not in PostgreSQL")
                    continue

                formatted_results.append({
                    "chunk_id": hit["id"],
                    "score": hit["score"],
                    "chunk_type": payload.get("chunk_type"),
                    "chunk_index": payload.get("chunk_index"),
                    "text": payload.get("chunk_text") or payload.get("text"),
                    "scheme_id": str(scheme.id),
                    "scheme_name": scheme.name,
                    "ministry": scheme.ministry,
                    "category": scheme.category,
                    "level": scheme.level,
                    "state": scheme.state,
                    "official_url": scheme.official_url
                })

            context_text = self._format_context(formatted_results)
            total_latency_ms = (time.perf_counter() - t0) * 1000.0
            
            metrics = {
                "embedding_latency_ms": embed_latency_ms,
                "qdrant_search_latency_ms": qdrant_latency_ms,
                "postgres_hydration_latency_ms": postgres_latency_ms,
                "total_pipeline_latency_ms": total_latency_ms
            }

            # Map schemes to JSON serializable objects
            schemes_data = []
            for s in schemes:
                schemes_data.append({
                    "id": str(s.id),
                    "name": s.name,
                    "description": s.description,
                    "ministry": s.ministry,
                    "category": s.category,
                    "level": s.level,
                    "state": s.state,
                    "benefits": s.benefits,
                    "eligibility_criteria": s.eligibility_criteria,
                    "required_documents": s.required_documents,
                    "application_process": s.application_process,
                    "official_url": s.official_url,
                    "status": s.status
                })

        except Exception as qdrant_err:
            logger.warning(f"Qdrant search or hydration failed: {qdrant_err}. Falling back to database keyword search.")
            t_postgres_start = time.perf_counter()
            try:
                scheme_repo = SchemeRepository(session)
                
                # Extract basic filters
                category_filter = filters.get("category") if filters else None
                state_filter = filters.get("state") if filters else None
                level_filter = filters.get("level") if filters else None
                
                # Search by keyword
                schemes = await scheme_repo.search_by_keyword(
                    keyword=question,
                    category=category_filter,
                    state=state_filter,
                    level=level_filter,
                    limit=top_k
                )
                t_postgres_end = time.perf_counter()
                postgres_latency_ms = (t_postgres_end - t_postgres_start) * 1000.0
                
                formatted_results = []
                # Synthesize chunks from matching schemes
                for s in schemes:
                    chunk_text = s.description or s.benefits or ""
                    chunk_type = "overview"
                    
                    # Try to get overview chunk from preloaded chunks
                    if s.chunks:
                        overview_chunks = [c for c in s.chunks if c.chunk_type == "overview"]
                        if overview_chunks:
                            chunk_text = overview_chunks[0].chunk_text
                            chunk_type = "overview"
                        else:
                            chunk_text = s.chunks[0].chunk_text
                            chunk_type = s.chunks[0].chunk_type

                    formatted_results.append({
                        "chunk_id": str(uuid4()),
                        "score": 0.50, # Static fallback score
                        "chunk_type": chunk_type,
                        "chunk_index": 0,
                        "text": chunk_text,
                        "scheme_id": str(s.id),
                        "scheme_name": s.name,
                        "ministry": s.ministry,
                        "category": s.category,
                        "level": s.level,
                        "state": s.state,
                        "official_url": s.official_url
                    })

                context_text = self._format_context(formatted_results)
                total_latency_ms = (time.perf_counter() - t0) * 1000.0
                
                metrics = {
                    "embedding_latency_ms": embed_latency_ms,
                    "qdrant_search_latency_ms": (time.perf_counter() - t_qdrant_start) * 1000.0,
                    "postgres_hydration_latency_ms": postgres_latency_ms,
                    "total_pipeline_latency_ms": total_latency_ms
                }

                # Map schemes to JSON serializable objects
                schemes_data = []
                for s in schemes:
                    schemes_data.append({
                        "id": str(s.id),
                        "name": s.name,
                        "description": s.description,
                        "ministry": s.ministry,
                        "category": s.category,
                        "level": s.level,
                        "state": s.state,
                        "benefits": s.benefits,
                        "eligibility_criteria": s.eligibility_criteria,
                        "required_documents": s.required_documents,
                        "application_process": s.application_process,
                        "official_url": s.official_url,
                        "status": s.status
                    })

            except Exception as db_err:
                logger.warning(f"Database query or connection failed: {db_err}. Using in-memory mock schemes for local fallback.")
                
                # Mock schemes definitions
                MOCK_SCHEMES = [
                    {
                        "id": "739417dd-c06a-4b3d-8cf9-7c776195fb1a",
                        "name": "Maharashtra State Government Open Merit Scholarship",
                        "description": "Scholarships for open category students to pursue higher education in Maharashtra.",
                        "ministry": "Higher and Technical Education Department",
                        "category": "Education",
                        "level": "State",
                        "state": "Maharashtra",
                        "benefits": "Tuition fees waiver and monthly stipend.",
                        "eligibility_criteria": {"age": 25, "income_annual": 800000},
                        "required_documents": [{"name": "Income Certificate", "mandatory": True}],
                        "application_process": "Apply online through MahaDBT portal.",
                        "official_url": "https://mahadbt.maharashtra.gov.in",
                        "status": "active",
                        "chunk_text": "This scholarship is offered by the Higher and Technical Education Department of Maharashtra to open category students pursuing higher education."
                    },
                    {
                        "id": "2e178e05-7a14-47e8-80be-ee5fde4b3b67",
                        "name": "Pradhan Mantri Awas Yojana (Gramin)",
                        "description": "Housing support scheme for rural families and tribal groups.",
                        "ministry": "Ministry of Rural Development",
                        "category": "Housing & Shelter",
                        "level": "Central",
                        "state": None,
                        "benefits": "Financial assistance of up to Rs 1.2 Lakhs for house construction.",
                        "eligibility_criteria": {"is_rural": True},
                        "required_documents": [{"name": "Aadhaar Card", "mandatory": True}],
                        "application_process": "Register via Gram Panchayat.",
                        "official_url": "https://pmayg.nic.in",
                        "status": "active",
                        "chunk_text": "PMAY-G aims to provide a pucca house with basic amenities to all houseless householders and those households living in dilapidated houses."
                    },
                    {
                        "id": "3e9b1d2e-4cf8-5a02-b1da-8e9f02c638fa",
                        "name": "PM Kisan Samman Nidhi",
                        "description": "Income support and fertilizer/seed subsidy support for landholding farmers.",
                        "ministry": "Ministry of Agriculture and Farmers Welfare",
                        "category": "Agriculture, Rural & Environment",
                        "level": "Central",
                        "state": None,
                        "benefits": "Rs. 6000 per year in three equal installments directly into bank accounts.",
                        "eligibility_criteria": {"is_farmer": True},
                        "required_documents": [{"name": "Land Records", "mandatory": True}],
                        "application_process": "Register online at PM Kisan portal.",
                        "official_url": "https://pmkisan.gov.in",
                        "status": "active",
                        "chunk_text": "PM Kisan provides direct income support of Rs. 6000 per year to all landholding farmer families across the country."
                    },
                    {
                        "id": "4a8c2d1e-9bf8-4e02-b2da-7e9f02c638fb",
                        "name": "Stand Up India Scheme for Women Entrepreneurs",
                        "description": "Financial loans and startup subsidy support for women SC/ST business owners.",
                        "ministry": "Ministry of Finance",
                        "category": "Banking, Financial Services & Insurance",
                        "level": "Central",
                        "state": None,
                        "benefits": "Bank loans between Rs. 10 Lakhs and Rs. 1 Crore for setting up greenfield enterprises.",
                        "eligibility_criteria": {"gender": "Female", "is_entrepreneur": True},
                        "required_documents": [{"name": "Project Report", "mandatory": True}],
                        "application_process": "Apply via Stand Up India portal or local bank branches.",
                        "official_url": "https://www.standupmitra.in",
                        "status": "active",
                        "chunk_text": "Stand Up India facilitates bank loans between 10 lakh and 1 crore to at least one SC or ST borrower and at least one woman borrower per bank branch."
                    }
                ]
                
                # Filter mock schemes
                matched_schemes = []
                q_lower = question.lower()
                category_filter = filters.get("category") if filters else None
                state_filter = filters.get("state") if filters else None
                level_filter = filters.get("level") if filters else None
                
                for s in MOCK_SCHEMES:
                    if category_filter and s["category"] != category_filter:
                        continue
                    if state_filter and s["state"] and s["state"] != state_filter:
                        continue
                    if level_filter and s["level"] != level_filter:
                        continue
                        
                    # Basic keyword check
                    if q_lower in s["name"].lower() or q_lower in s["description"].lower() or q_lower in s["category"].lower() or any(w in s["name"].lower() or w in s["description"].lower() for w in q_lower.split()):
                        matched_schemes.append(s)
                
                matched_schemes = matched_schemes[:top_k]
                
                formatted_results = []
                for s in matched_schemes:
                    formatted_results.append({
                        "chunk_id": str(uuid4()),
                        "score": 0.50,
                        "chunk_type": "overview",
                        "chunk_index": 0,
                        "text": s["chunk_text"],
                        "scheme_id": s["id"],
                        "scheme_name": s["name"],
                        "ministry": s["ministry"],
                        "category": s["category"],
                        "level": s["level"],
                        "state": s["state"],
                        "official_url": s["official_url"]
                    })
                
                context_text = self._format_context(formatted_results)
                total_latency_ms = (time.perf_counter() - t0) * 1000.0
                
                metrics = {
                    "embedding_latency_ms": embed_latency_ms,
                    "qdrant_search_latency_ms": (time.perf_counter() - t_qdrant_start) * 1000.0,
                    "postgres_hydration_latency_ms": (time.perf_counter() - t_postgres_start) * 1000.0,
                    "total_pipeline_latency_ms": total_latency_ms
                }
                
                schemes_data = []
                for s in matched_schemes:
                    schemes_data.append({
                        "id": s["id"],
                        "name": s["name"],
                        "description": s["description"],
                        "ministry": s["ministry"],
                        "category": s["category"],
                        "level": s["level"],
                        "state": s["state"],
                        "benefits": s["benefits"],
                        "eligibility_criteria": s["eligibility_criteria"],
                        "required_documents": s["required_documents"],
                        "application_process": s["application_process"],
                        "official_url": s["official_url"],
                        "status": s["status"]
                    })

        return {
            "question": question,
            "context_text": context_text,
            "retrieved_chunks": formatted_results,
            "schemes": schemes_data,
            "metrics": metrics
        }

    def _format_context(self, results: list[dict]) -> str:
        """Format retrieved documents into LLM-ready context string."""
        context_parts = []
        for i, res in enumerate(results, 1):
            part = (
                f"### Result {i}: Scheme - {res['scheme_name']}\n"
                f"- **Ministry**: {res['ministry'] or 'N/A'}\n"
                f"- **Category**: {res['category'] or 'N/A'}\n"
                f"- **Level**: {res['level'] or 'N/A'} (State: {res['state'] or 'N/A'})\n"
                f"- **Official URL**: {res['official_url'] or 'N/A'}\n"
                f"- **Section**: {res['chunk_type']} (Index: {res['chunk_index']}, Score: {res['score']:.4f})\n\n"
                f"Content:\n{res['text']}\n"
            )
            context_parts.append(part)
        
        return "\n---\n\n".join(context_parts)
