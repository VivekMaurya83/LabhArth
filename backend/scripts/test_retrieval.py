"""
LabhArth AI — RAG Retrieval Verification Script
=================================================
Verifies query embedding, similarity search in Qdrant, relational hydration from PostgreSQL,
metadata filtering, and latency tracking across multiple query scenarios.
"""

import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
from backend.database.connection import async_session_factory
from backend.models.db_models import Scheme
from backend.services.retrieval_service import RetrievalService
from backend.utils.logger import logger

# Set logging level to WARNING for cleaner test output
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def check_db_stats():
    """Prints database stats to verify content and category names."""
    print("\n=== PostgreSQL Database Quick Check ===")
    try:
        async with async_session_factory() as session:
            # Count total schemes
            res_count = await session.execute(select(Scheme))
            schemes = res_count.scalars().all()
            print(f"Total schemes in DB: {len(schemes)}")
            
            # Print categories
            categories = set(s.category for s in schemes if s.category)
            print(f"Unique categories in DB: {list(categories)}")
            
            # Print states
            states = set(s.state for s in schemes if s.state)
            print(f"Unique states in DB: {list(states)}")
            
            # Print a few scheme details
            print("\nSample Schemes in DB:")
            for s in schemes[:5]:
                print(f"  - [{s.id}] Name: '{s.name}' | State: '{s.state}' | Category: '{s.category}'")
    except Exception as e:
        import traceback
        print(f"[ERROR] Error checking DB stats: {repr(e)}")
        traceback.print_exc()
    print("=" * 40 + "\n")


async def run_scenario(retrieval_service: RetrievalService, name: str, query: str, filters: dict = None):
    print("\n" + "=" * 80)
    print(f"SCENARIO: {name}")
    print(f"Query:    '{query}'")
    print(f"Filters:  {filters}")
    print("=" * 80)

    res = await retrieval_service.retrieve_context(
        query=query,
        filters=filters,
        top_k=3,
        score_threshold=0.30  # Lower threshold to ensure matches are found in small test collection
    )

    if "error" in res:
        print(f"[ERROR] Error: {res['error']}")
        return

    metrics = res.get("metrics", {})
    print("\n[TIME] Execution Metrics:")
    print(f"  - Embedding Latency:     {metrics.get('embedding_latency_ms', 0):.2f} ms")
    print(f"  - Qdrant Search Latency: {metrics.get('qdrant_search_latency_ms', 0):.2f} ms")
    print(f"  - Postgres Hydration:    {metrics.get('postgres_hydration_latency_ms', 0):.2f} ms")
    print(f"  - Total Pipeline Latency: {metrics.get('total_pipeline_latency_ms', 0):.2f} ms")

    chunks = res.get("retrieved_chunks", [])
    print(f"\n[MATCHES] Matches Found: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n  [{i}] Scheme Name: {chunk['scheme_name']}")
        print(f"      Score:       {chunk['score']:.4f}")
        print(f"      Section:     {chunk['chunk_type']} (Index: {chunk['chunk_index']})")
        print(f"      Ministry:    {chunk['ministry']}")
        print(f"      Level/State: {chunk['level']} (State: {chunk['state']})")
        preview = chunk["text"][:150].replace("\n", " ") + "..."
        print(f"      Preview:     {preview}")

    print("\n[CONTEXT] Formatted Context Length:", len(res.get("context_text", "")))


async def main():
    # Verify DB content first
    await check_db_stats()

    print("Initializing RetrievalService...")
    retrieval_service = RetrievalService()

    scenarios = [
        {
            "name": " Maharashtra Student Scholarship",
            "query": "scholarships and educational benefits for students in maharashtra",
            "filters": {"state": "Maharashtra", "category": "Education"}
        },
        {
            "name": " Housing Schemes for Tribal / Rural Families",
            "query": "housing scheme or raw shelter benefits for tribal families",
            "filters": {"category": "Housing & Shelter"}
        },
        {
            "name": " Agricultural Subsidies and Fertilizers",
            "query": "farmer subsidies seed fertilizer support",
            "filters": {"category": "Agriculture, Rural & Environment"}
        },
        {
            "name": " Women Entrepreneurship & Business Loans",
            "query": "business loan startup subsidy support for women",
            "filters": {"category": "Banking, Financial Services & Insurance"}
        }
    ]

    for scenario in scenarios:
        await run_scenario(
            retrieval_service,
            scenario["name"],
            scenario["query"],
            scenario["filters"]
        )


if __name__ == "__main__":
    asyncio.run(main())
