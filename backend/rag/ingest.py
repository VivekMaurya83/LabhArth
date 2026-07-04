"""
LabhArth AI — ETL Ingestion Pipeline
======================================
Orchestrates raw PDF downloads, text extraction, semantic chunking, 
Gemini structured parsing, PostgreSQL indexing, and Qdrant vector upserts.
Supports checkpoint resume and multi-key API rotation.
"""

import argparse
import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import select, func

# Load environment variables first
load_dotenv()

from backend.database.connection import init_db, async_session_factory
from backend.models.db_models import Scheme, SchemeChunk, IngestionRun
from backend.rag.dataset_downloader import download_dataset
from backend.rag.chunker import DocumentChunker, NAMESPACE_LABHARTH_STR
from backend.rag.embeddings import EmbeddingService, ExtractionService
from backend.rag.retriever import QdrantRetriever
from backend.utils.logger import logger

# Namespace UUID for deterministic Qdrant point IDs
NAMESPACE_LABHARTH = uuid.UUID(NAMESPACE_LABHARTH_STR)


async def check_scheme_exists(session, url: str) -> Optional[Scheme]:
    """Check if the scheme has already been created in PostgreSQL."""
    query = select(Scheme).where(Scheme.official_url == url)
    result = await session.execute(query)
    return result.scalars().first()


async def check_chunks_indexed(session, scheme_id: uuid.UUID) -> bool:
    """Check if all chunks for a scheme are already indexed in Qdrant successfully."""
    query = select(func.count(SchemeChunk.id)).where(
        (SchemeChunk.scheme_id == scheme_id) & 
        (SchemeChunk.embedding_status == "success")
    )
    result = await session.execute(query)
    count = result.scalar()
    return count > 0


async def process_single_scheme(
    idx: int,
    total_files: int,
    pdf_path: Path,
    sem: asyncio.Semaphore,
    run_id: uuid.UUID,
    chunker: DocumentChunker,
    extractor: ExtractionService,
    embedder: EmbeddingService,
    retriever: QdrantRetriever,
    skip_extraction: bool,
    progress: dict
):
    """Processes a single scheme PDF file asynchronously with concurrency limiting."""
    file_name = pdf_path.name
    url = f"https://www.myscheme.gov.in/schemes/{pdf_path.stem}"

    async with sem:
        logger.info(f"[{idx+1}/{total_files}] Starting processing for: {file_name}")
        
        async with async_session_factory() as session:
            # Check for existing scheme for Checkpoint Resume
            try:
                existing_scheme = await check_scheme_exists(session, url)
                if existing_scheme:
                    # Check if chunks are already indexed successfully
                    already_indexed = await check_chunks_indexed(session, existing_scheme.id)
                    if already_indexed:
                        logger.info(f"Scheme '{existing_scheme.name}' is already fully indexed. Skipping.")
                        progress["skipped"] += 1
                        return
                    else:
                        logger.info(f"Scheme record found for '{existing_scheme.name}' but chunks are not indexed. Re-indexing.")
            except Exception as e:
                logger.error(f"Error querying checkpoint database for {file_name}: {e}")
                return

            # 2. Extract raw text from PDF
            try:
                raw_text = chunker.extract_text(pdf_path)
            except Exception as e:
                logger.error(f"Failed to extract text from {file_name}: {e}. Skipping file.")
                return

            if not raw_text.strip():
                logger.warning(f"Empty text in PDF {file_name}. Skipping file.")
                return

            # 3. Semantic Segment Parsing
            parsed_sections = chunker.parse_sections(raw_text)
            
            # 4. Gemini Structured JSONB Extraction
            try:
                if skip_extraction:
                    logger.warning("Skipping Gemini structured extraction. Using default placeholders.")
                    name = pdf_path.stem.replace("-", " ").title()
                    category = "other"
                    level = "central"
                    state = None
                    ministry = "Unknown Ministry"
                    eligibility_json = {"rules": [], "additional_notes": "", "raw_text": parsed_sections.get("eligibility", "")}
                    documents_json = []
                else:
                    structured_data = extractor.extract_scheme_metadata(file_name, raw_text)
                    name = structured_data.name
                    category = structured_data.category
                    level = structured_data.level
                    state = structured_data.state
                    ministry = structured_data.ministry
                    eligibility_json = structured_data.eligibility.model_dump()
                    documents_json = [doc.model_dump() for doc in structured_data.required_documents]
            except Exception as e:
                err_msg = str(e).lower()
                if "quota" in err_msg or "429" in err_msg or "exhausted" in err_msg:
                    logger.error(f"Gemini API Quota Exceeded during extraction: {e}")
                    raise e
                logger.error(f"Gemini extraction failed for {file_name}: {e}. Skipping file.")
                return

            # 5. Insert or Update Scheme in PostgreSQL
            try:
                if existing_scheme:
                    scheme = existing_scheme
                    scheme.name = name
                    scheme.description = parsed_sections.get("overview", "")
                    scheme.ministry = ministry
                    scheme.category = category
                    scheme.level = level
                    scheme.state = state
                    scheme.eligibility_criteria = eligibility_json
                    scheme.benefits = parsed_sections.get("benefits", "")
                    scheme.required_documents = documents_json
                    scheme.application_process = parsed_sections.get("application", "")
                    progress["updated"] += 1
                else:
                    scheme = Scheme(
                        name=name,
                        description=parsed_sections.get("overview", ""),
                        ministry=ministry,
                        category=category,
                        level=level,
                        state=state,
                        eligibility_criteria=eligibility_json,
                        benefits=parsed_sections.get("benefits", ""),
                        required_documents=documents_json,
                        application_process=parsed_sections.get("application", ""),
                        official_url=url,
                        status="active"
                    )
                    session.add(scheme)
                    progress["created"] += 1

                # Flush session to get the scheme ID
                await session.flush()
                scheme_id = scheme.id

                # Clean old chunks if re-indexing
                if existing_scheme:
                    from sqlalchemy import delete
                    await session.execute(delete(SchemeChunk).where(SchemeChunk.scheme_id == scheme_id))

                # 6. Generate Section-based Chunks
                chunks_data = chunker.chunk_scheme(name, category, level if level == "central" else state, ministry, parsed_sections)
                db_chunks = []

                for chk in chunks_data:
                    point_id = uuid.uuid5(NAMESPACE_LABHARTH, f"{scheme_id}:{chk['chunk_type']}:{chk['chunk_index']}")
                    
                    db_chunk = SchemeChunk(
                        scheme_id=scheme_id,
                        chunk_type=chk["chunk_type"],
                        chunk_index=chk["chunk_index"],
                        chunk_text=chk["chunk_text"],
                        token_count=chk["token_count"],
                        qdrant_point_id=point_id,
                        embedding_status="pending",
                        ingestion_run_id=run_id
                    )
                    session.add(db_chunk)
                    db_chunks.append(db_chunk)
                    progress["chunks_created"] += 1

                await session.flush()
            except Exception as e:
                logger.error(f"PostgreSQL operations failed for {file_name}: {e}. Rollback transaction.")
                await session.rollback()
                return

            # 7. Generate Chunks Vector Embeddings (Batch call)
            chunk_texts = [chk.chunk_text for chk in db_chunks]
            try:
                logger.debug(f"Generating vectors for {len(chunk_texts)} chunks of {name}...")
                vectors = await embedder.embed_batch(chunk_texts)
                progress["embeddings_generated"] += len(vectors)
            except Exception as e:
                logger.error(f"Embedding batch generation failed for {file_name}: {e}. Rollback transaction.")
                await session.rollback()
                return

            # 8. Upsert Vectors to Qdrant
            qdrant_docs = []
            for chk in db_chunks:
                qdrant_docs.append({
                    "scheme_id": str(scheme_id),
                    "pg_chunk_id": str(chk.id),
                    "qdrant_point_id": str(chk.qdrant_point_id),
                    "scheme_name": name,
                    "category": category,
                    "level": level,
                    "state": state,
                    "chunk_type": chk.chunk_type,
                    "chunk_index": chk.chunk_index,
                    "chunk_text": chk.chunk_text,
                    "ministry": ministry,
                    "ingestion_run_id": str(run_id),
                    "ingested_at": datetime.utcnow().isoformat()
                })

            try:
                await retriever.upsert_documents(qdrant_docs, vectors)
                progress["qdrant_points_upserted"] += len(vectors)
                
                # Update database chunk status on success
                for chk in db_chunks:
                    chk.embedding_status = "success"
            except Exception as e:
                logger.error(f"Qdrant indexing failed for {file_name}: {e}. Rollback transaction.")
                await session.rollback()
                return

            # Commit transaction for this scheme (Checkpoint secured!)
            await session.commit()
            logger.info(f"Successfully processed and indexed scheme: {name}")


async def run_ingestion(
    limit: Optional[int] = None,
    skip_extraction: bool = False,
    worker_count: int = 2,
):
    """
    Main ETL orchestration loop utilizing concurrent workers.
    """
    logger.info("Initializing LabhArth AI Ingestion Pipeline...")
    
    # Ensure Postgres tables exist
    await init_db()
    
    # Download dataset
    try:
        pdf_files = download_dataset()
    except Exception as e:
        logger.error(f"Dataset acquisition failed: {e}")
        return

    if limit:
        logger.info(f"Limiting ingestion run to first {limit} schemes.")
        pdf_files = pdf_files[:limit]

    # Initialize services
    chunker = DocumentChunker()
    extractor = ExtractionService(delay_seconds=1)
    embedder = EmbeddingService()
    retriever = QdrantRetriever()

    # Create ingestion run audit trail
    run_id = uuid.uuid4()
    started_at = datetime.utcnow()
    
    async with async_session_factory() as audit_session:
        run_record = IngestionRun(
            id=run_id,
            source_type="huggingface_pdf",
            source_path="shrijayan/gov_myscheme/text_data",
            total_schemes=len(pdf_files),
            status="running",
            started_at=started_at
        )
        audit_session.add(run_record)
        await audit_session.commit()
    
    logger.info(f"Started Ingestion Run ID: {run_id}")

    # Track progress counts in a thread-safe dictionary
    progress = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "chunks_created": 0,
        "embeddings_generated": 0,
        "qdrant_points_upserted": 0
    }

    # Set concurrency limit (Semaphore)
    # Keep Gemini pressure low by default; override with --workers when needed.
    sem = asyncio.Semaphore(max(1, worker_count))

    try:
        # Create asynchronous tasks for all files
        tasks = [
            process_single_scheme(
                idx=idx,
                total_files=len(pdf_files),
                pdf_path=pdf_path,
                sem=sem,
                run_id=run_id,
                chunker=chunker,
                extractor=extractor,
                embedder=embedder,
                retriever=retriever,
                skip_extraction=skip_extraction,
                progress=progress
            )
            for idx, pdf_path in enumerate(pdf_files)
        ]

        # Execute concurrent pipeline tasks
        await asyncio.gather(*tasks)

        # Update run status to completed on success
        async with async_session_factory() as audit_session:
            run_rec = await audit_session.get(IngestionRun, run_id)
            if run_rec:
                run_rec.status = "completed"
                run_rec.schemes_created = progress["created"]
                run_rec.schemes_updated = progress["updated"]
                run_rec.schemes_skipped = progress["skipped"]
                run_rec.chunks_created = progress["chunks_created"]
                run_rec.embeddings_generated = progress["embeddings_generated"]
                run_rec.qdrant_points_upserted = progress["qdrant_points_upserted"]
                run_rec.completed_at = datetime.utcnow()
                await audit_session.commit()
        
        logger.info("Ingestion pipeline finished successfully!")
        logger.info(
            f"Stats - Created: {progress['created']}, Updated: {progress['updated']}, "
            f"Skipped: {progress['skipped']}, Chunks: {progress['chunks_created']}, "
            f"Points: {progress['qdrant_points_upserted']}"
        )

    except Exception as exc:
        err_msg = str(exc)
        logger.error(f"Ingestion run interrupted by exception: {exc}")
        
        async with async_session_factory() as audit_session:
            run_rec = await audit_session.get(IngestionRun, run_id)
            if run_rec:
                run_rec.status = "failed"
                run_rec.error_message = err_msg[:1000]
                run_rec.schemes_created = progress["created"]
                run_rec.schemes_updated = progress["updated"]
                run_rec.schemes_skipped = progress["skipped"]
                run_rec.chunks_created = progress["chunks_created"]
                run_rec.embeddings_generated = progress["embeddings_generated"]
                run_rec.qdrant_points_upserted = progress["qdrant_points_upserted"]
                run_rec.completed_at = datetime.utcnow()
                await audit_session.commit()
        
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LabhArth AI — Ingestion Pipeline CLI")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of schemes processed (for dry run).")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip Gemini extraction and use placeholders (for quick debugging).")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of concurrent schemes to process at once. Lower values reduce Gemini quota pressure.",
    )
    args = parser.parse_args()

    asyncio.run(
        run_ingestion(
            limit=args.limit,
            skip_extraction=args.skip_extraction,
            worker_count=args.workers,
        )
    )
