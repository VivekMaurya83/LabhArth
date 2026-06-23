-- LabhArth AI — Ingestion & Traceability Schema Migration
-- Neon PostgreSQL Migration

-- 1. Create Ingestion Runs Audit Table
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type     VARCHAR(100) NOT NULL,            -- e.g. 'huggingface_pdf'
    source_path     VARCHAR(500),
    total_schemes   INTEGER DEFAULT 0,
    schemes_created INTEGER DEFAULT 0,
    schemes_updated INTEGER DEFAULT 0,
    schemes_skipped INTEGER DEFAULT 0,
    chunks_created  INTEGER DEFAULT 0,
    embeddings_generated INTEGER DEFAULT 0,
    qdrant_points_upserted INTEGER DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'running',    -- running, completed, failed
    error_message   TEXT,
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP
);

-- 2. Create Scheme Chunks Traceability Table
CREATE TABLE IF NOT EXISTS scheme_chunks (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id         UUID NOT NULL REFERENCES schemes(id) ON DELETE CASCADE,
    chunk_type        VARCHAR(50) NOT NULL,            -- overview, eligibility, benefits, documents, application, combined
    chunk_index       INTEGER NOT NULL DEFAULT 0,
    chunk_text        TEXT NOT NULL,
    token_count       INTEGER,
    qdrant_point_id   UUID,                             -- deterministic UUID5 mapped to Qdrant point
    embedding_status  VARCHAR(20) DEFAULT 'pending',   -- pending, success, failed
    ingestion_run_id  UUID REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_scheme_chunk UNIQUE(scheme_id, chunk_type, chunk_index)
);

-- 3. Create Indexes for High Retrieval Speed
CREATE INDEX IF NOT EXISTS idx_chunks_scheme ON scheme_chunks(scheme_id);
CREATE INDEX IF NOT EXISTS idx_chunks_type ON scheme_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_chunks_qdrant ON scheme_chunks(qdrant_point_id);
CREATE INDEX IF NOT EXISTS idx_chunks_status ON scheme_chunks(embedding_status);
