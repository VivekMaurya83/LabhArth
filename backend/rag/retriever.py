"""
LabhArth AI — Retriever
=========================
Vector similarity search using Qdrant Cloud.
"""

import uuid
from typing import Any, Dict, List, Optional

from backend.utils.config import get_settings
from backend.utils.logger import logger


class QdrantRetriever:
    """
    Retrieve relevant scheme documents from Qdrant vector store.

    Performs semantic search over scheme embeddings and returns
    the most relevant document chunks for LLM context augmentation.
    """

    def __init__(self):
        self.settings = get_settings()
        self._client = None  # Lazy initialization
        self.collection_name = self.settings.qdrant_collection_name
        logger.info(f"QdrantRetriever initialized for collection: {self.collection_name}")

    async def _get_client(self):
        """Lazily initialize Qdrant client."""
        if self._client is None:
            from qdrant_client import AsyncQdrantClient

            url = self.settings.qdrant_url
            api_key = self.settings.qdrant_api_key
            timeout = self.settings.rag_timeout_seconds

            if url and "localhost" not in url:
                logger.info(f"Connecting to Qdrant Cloud cluster at {url[:30]}...")
                self._client = AsyncQdrantClient(url=url, api_key=api_key, timeout=timeout)
            else:
                logger.info("Connecting to local Qdrant instance at localhost:6333...")
                self._client = AsyncQdrantClient(host="localhost", port=6333, timeout=timeout)
        return self._client

    async def ensure_collection_exists(self) -> None:
        """Create Qdrant collection if it does not exist, and build keyword indexes."""
        client = await self._get_client()
        from qdrant_client.models import Distance, VectorParams

        try:
            exists = await client.collection_exists(self.collection_name)
            if not exists:
                logger.info(f"Creating collection '{self.collection_name}' with 768 dimensions (Cosine)...")
                await client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                logger.info(f"Collection '{self.collection_name}' created successfully.")
                await self.create_payload_indexes()
            else:
                logger.debug(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Error checking/creating Qdrant collection: {e}")
            raise

    async def create_payload_indexes(self) -> None:
        """Create indexes on payload fields for high-performance filtering."""
        client = await self._get_client()
        from qdrant_client.models import PayloadSchemaType

        fields = ["state", "category", "level", "chunk_type", "scheme_id", "ministry"]
        for field in fields:
            try:
                await client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                logger.info(f"Created keyword index on payload field: {field}")
            except Exception as e:
                logger.error(f"Failed to create payload index on {field}: {e}")

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.65,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Qdrant using direct HTTP REST API.

        Args:
            query_vector: Query embedding vector
            limit: Maximum results to return
            score_threshold: Minimum similarity score
            filters: Optional Qdrant payload filters

        Returns:
            List of matching documents with scores
        """
        import httpx

        # Build URL
        url = self.settings.qdrant_url
        endpoint = f"{url}/collections/{self.collection_name}/points/search"

        # Headers
        headers = {
            "Content-Type": "application/json"
        }
        if self.settings.qdrant_api_key:
            headers["api-key"] = self.settings.qdrant_api_key

        # Build filter conditions
        conditions = []

        if filters:
            # Handle state filter: returns central schemes (state is null) OR state matching user's state
            if "state" in filters:
                state_val = filters["state"]
                if state_val:
                    conditions.append(
                        {
                            "should": [
                                {"key": "state", "match": {"value": state_val}},
                                {"is_empty": {"key": "state"}}
                            ]
                        }
                    )
            
            # Handle category filter
            if "category" in filters:
                category_val = filters["category"]
                if category_val:
                    # Convert to lowercase to match payloads in Qdrant (which are lowercased)
                    conditions.append(
                        {
                            "key": "category",
                            "match": {"value": category_val.lower()}
                        }
                    )
            
            # Handle chunk type filter
            if "chunk_type" in filters:
                chunk_type_val = filters["chunk_type"]
                if chunk_type_val:
                    if isinstance(chunk_type_val, list):
                        conditions.append(
                            {
                                "key": "chunk_type",
                                "match": {"any": chunk_type_val}
                            }
                        )
                    else:
                        conditions.append(
                            {
                                "key": "chunk_type",
                                "match": {"value": chunk_type_val}
                            }
                        )

            # Handle level filter (State vs Central)
            if "level" in filters:
                level_val = filters["level"]
                if level_val:
                    conditions.append(
                        {
                            "key": "level",
                            "match": {"value": level_val.lower()}
                        }
                    )

            # Handle ministry filter
            if "ministry" in filters:
                ministry_val = filters["ministry"]
                if ministry_val:
                    conditions.append(
                        {
                            "key": "ministry",
                            "match": {"value": ministry_val}
                        }
                    )

            # Handle explicit scheme_id scoping
            if "scheme_id" in filters:
                scheme_id_val = filters["scheme_id"]
                if scheme_id_val:
                    conditions.append(
                        {
                            "key": "scheme_id",
                            "match": {"value": str(scheme_id_val)}
                        }
                    )

        qdrant_filter = {"must": conditions} if conditions else None

        # Build payload
        payload = {
            "vector": query_vector,
            "limit": limit,
            "score_threshold": score_threshold,
            "with_payload": True
        }
        if qdrant_filter:
            payload["filter"] = qdrant_filter

        try:
            logger.info(f"Querying Qdrant similarity search via HTTP (limit={limit}, threshold={score_threshold})...")
            
            async with httpx.AsyncClient(http2=False, timeout=self.settings.rag_timeout_seconds) as http_client:
                response = await http_client.post(endpoint, json=payload, headers=headers)
                
                if response.status_code != 200:
                    raise RuntimeError(f"Qdrant REST API returned status code {response.status_code}: {response.text}")
                
                data = response.json()
                search_results = data.get("result", [])
            
            formatted_results = []
            for hit in search_results:
                formatted_results.append({
                    "id": hit.get("id"),
                    "score": hit.get("score"),
                    "payload": hit.get("payload", {})
                })
            
            logger.info(f"Qdrant returned {len(formatted_results)} results.")
            return formatted_results
        except Exception as e:
            logger.error(f"Qdrant search query failed: {e}")
            raise

    async def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        vectors: List[List[float]],
    ) -> None:
        """
        Insert or update documents in Qdrant.

        Args:
            documents: List of document payloads
            vectors: Corresponding embedding vectors
        """
        if not documents or not vectors:
            logger.warning("Empty documents or vectors passed to Qdrant upsert.")
            return

        client = await self._get_client()
        from qdrant_client.models import PointStruct

        await self.ensure_collection_exists()

        points = []
        # NAMESPACE defined for platform point ID matching
        NAMESPACE_LABHARTH = uuid.UUID("3c7b2e3d-d19a-4f51-b0db-6a7f85e493cc")

        for doc, vec in zip(documents, vectors):
            point_id = doc.get("qdrant_point_id")
            
            # Generate deterministic UUIDv5 if not already provided
            if not point_id:
                scheme_id = str(doc.get("scheme_id"))
                chunk_type = str(doc.get("chunk_type"))
                chunk_index = str(doc.get("chunk_index", 0))
                point_id = uuid.uuid5(NAMESPACE_LABHARTH, f"{scheme_id}:{chunk_type}:{chunk_index}")
            elif isinstance(point_id, str):
                point_id = uuid.UUID(point_id)

            payload = {
                "scheme_id": str(doc.get("scheme_id")),
                "pg_chunk_id": str(doc.get("pg_chunk_id")),
                "scheme_name": doc.get("scheme_name"),
                "category": doc.get("category"),
                "level": doc.get("level"),
                "state": doc.get("state"),  # Mapped as None for central
                "chunk_type": doc.get("chunk_type"),
                "chunk_index": int(doc.get("chunk_index", 0)),
                "chunk_text": doc.get("chunk_text"),
                "ministry": doc.get("ministry"),
                "ingestion_run_id": str(doc.get("ingestion_run_id")) if doc.get("ingestion_run_id") else None,
                "ingested_at": doc.get("ingested_at")
            }

            points.append(
                PointStruct(
                    id=str(point_id),
                    vector=vec,
                    payload=payload
                )
            )

        try:
            logger.info(f"Upserting {len(points)} points into Qdrant collection '{self.collection_name}'...")
            await client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True
            )
            logger.info(f"Qdrant indexing complete for {len(points)} points.")
        except Exception as e:
            logger.error(f"Failed to upsert points into Qdrant: {e}")
            raise
