-- Migration: 001_initial_schema.sql
-- Description: Create core tables for funding opportunities and awards
-- Author: GovFunding Core Team
-- Date: 2025-10-10
-- Dependencies: None
-- Rollback: See 001_initial_schema_rollback.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For full-text search optimization

-- ============================================================================
-- Table: funding_opportunities
-- Description: Stores NSF and federal grant opportunities from Grants.gov
-- ============================================================================
CREATE TABLE funding_opportunities (
    -- Primary Key
    opportunity_id TEXT PRIMARY KEY,

    -- Core Metadata
    title TEXT NOT NULL,
    summary TEXT,
    agency_code TEXT,
    agency_name TEXT,

    -- Categorization
    cfda_numbers TEXT[] DEFAULT '{}',
    funding_category TEXT,
    instrument_types TEXT[] DEFAULT '{}',

    -- Financial Information
    award_floor NUMERIC(15, 2),
    award_ceiling NUMERIC(15, 2),
    estimated_total NUMERIC(15, 2),

    -- Timeline
    post_date DATE,
    close_date DATE,
    archive_date DATE,

    -- Detailed Information
    eligibility_text TEXT,
    cost_sharing_required BOOLEAN DEFAULT false,

    -- System Fields
    content_hash TEXT, -- For change detection (MD5 of title+summary)
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Computed Fields (via trigger)
    deadline_status TEXT GENERATED ALWAYS AS (
        CASE
            WHEN close_date IS NULL THEN 'unknown'
            WHEN close_date < CURRENT_DATE THEN 'closed'
            WHEN close_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'closing_soon'
            ELSE 'open'
        END
    ) STORED,

    award_midpoint NUMERIC(15, 2) GENERATED ALWAYS AS (
        CASE
            WHEN award_floor IS NOT NULL AND award_ceiling IS NOT NULL
            THEN (award_floor + award_ceiling) / 2
            ELSE NULL
        END
    ) STORED,

    -- Constraints
    CONSTRAINT check_award_range CHECK (
        award_floor IS NULL OR award_ceiling IS NULL OR award_floor <= award_ceiling
    ),
    CONSTRAINT check_close_date_after_post CHECK (
        post_date IS NULL OR close_date IS NULL OR close_date >= post_date
    )
);

-- Indexes for funding_opportunities
CREATE INDEX idx_opportunities_agency ON funding_opportunities(agency_code);
CREATE INDEX idx_opportunities_close_date ON funding_opportunities(close_date);
CREATE INDEX idx_opportunities_deadline_status ON funding_opportunities(deadline_status);
CREATE INDEX idx_opportunities_post_date ON funding_opportunities(post_date DESC);
CREATE INDEX idx_opportunities_funding_category ON funding_opportunities(funding_category);
CREATE INDEX idx_opportunities_last_synced ON funding_opportunities(last_synced_at DESC);

-- Full-text search index on title and summary
CREATE INDEX idx_opportunities_title_search ON funding_opportunities USING GIN (to_tsvector('english', title));
CREATE INDEX idx_opportunities_summary_search ON funding_opportunities USING GIN (to_tsvector('english', COALESCE(summary, '')));

-- Composite index for common queries
CREATE INDEX idx_opportunities_agency_close_date ON funding_opportunities(agency_code, close_date);

-- ============================================================================
-- Table: nsf_awards
-- Description: Historical NSF award data for trend analysis
-- ============================================================================
CREATE TABLE nsf_awards (
    -- Primary Key
    nsf_award_id TEXT PRIMARY KEY,

    -- Core Information
    award_title TEXT NOT NULL,
    pi_names TEXT[] DEFAULT '{}',

    -- Organization
    organization_code TEXT,
    organization_name TEXT,
    directorate TEXT,
    division TEXT,

    -- Timeline & Funding
    start_date DATE,
    end_date DATE,
    award_amount NUMERIC(15, 2),

    -- Content
    abstract_text TEXT,
    program_reference_codes TEXT[] DEFAULT '{}',

    -- System Fields
    publication_date DATE,
    content_hash TEXT,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT check_award_dates CHECK (
        start_date IS NULL OR end_date IS NULL OR end_date >= start_date
    )
);

-- Indexes for nsf_awards
CREATE INDEX idx_awards_directorate ON nsf_awards(directorate);
CREATE INDEX idx_awards_division ON nsf_awards(division);
CREATE INDEX idx_awards_start_date ON nsf_awards(start_date DESC);
CREATE INDEX idx_awards_award_amount ON nsf_awards(award_amount DESC);
CREATE INDEX idx_awards_publication_date ON nsf_awards(publication_date DESC);

-- Full-text search on award title and abstract
CREATE INDEX idx_awards_title_search ON nsf_awards USING GIN (to_tsvector('english', award_title));
CREATE INDEX idx_awards_abstract_search ON nsf_awards USING GIN (to_tsvector('english', COALESCE(abstract_text, '')));

-- ============================================================================
-- Table: opportunity_chunks
-- Description: Text chunks for RAG vector search
-- ============================================================================
CREATE TABLE opportunity_chunks (
    -- Primary Key
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Key
    opportunity_id TEXT NOT NULL REFERENCES funding_opportunities(opportunity_id) ON DELETE CASCADE,

    -- Chunk Data
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL, -- MD5 of content for change detection

    -- Metadata for filtering
    chunk_type TEXT DEFAULT 'summary', -- 'summary' | 'eligibility' | 'requirements' | 'timeline'

    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one opportunity cannot have duplicate chunk_index
    CONSTRAINT unique_opportunity_chunk UNIQUE (opportunity_id, chunk_index),

    -- Constraint: chunk_index must be >= 0
    CONSTRAINT check_chunk_index CHECK (chunk_index >= 0)
);

-- Indexes for opportunity_chunks
CREATE INDEX idx_chunks_opportunity_id ON opportunity_chunks(opportunity_id);
CREATE INDEX idx_chunks_content_hash ON opportunity_chunks(content_hash);
CREATE INDEX idx_chunks_chunk_type ON opportunity_chunks(chunk_type);

-- ============================================================================
-- Table: opportunity_updates
-- Description: Audit log of opportunity changes for change feed
-- ============================================================================
CREATE TABLE opportunity_updates (
    -- Primary Key
    update_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Key
    opportunity_id TEXT NOT NULL REFERENCES funding_opportunities(opportunity_id) ON DELETE CASCADE,

    -- Update Information
    update_type TEXT NOT NULL CHECK (update_type IN ('created', 'modified', 'archived')),
    update_payload JSONB, -- Changed fields stored as JSON

    -- System Fields
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for opportunity_updates
CREATE INDEX idx_updates_opportunity_id ON opportunity_updates(opportunity_id);
CREATE INDEX idx_updates_updated_at ON opportunity_updates(updated_at DESC);
CREATE INDEX idx_updates_update_type ON opportunity_updates(update_type);

-- ============================================================================
-- Table: etl_runs
-- Description: ETL execution tracking and monitoring
-- ============================================================================
CREATE TABLE etl_runs (
    -- Primary Key
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Run Metadata
    run_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed', 'partial')),

    -- Metrics
    opportunities_extracted INTEGER DEFAULT 0,
    opportunities_created INTEGER DEFAULT 0,
    opportunities_updated INTEGER DEFAULT 0,
    awards_extracted INTEGER DEFAULT 0,
    awards_created INTEGER DEFAULT 0,
    awards_updated INTEGER DEFAULT 0,

    -- Execution Info
    duration_seconds INTEGER,
    error_message TEXT,
    error_trace TEXT,

    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for etl_runs
CREATE INDEX idx_etl_runs_run_date ON etl_runs(run_date DESC);
CREATE INDEX idx_etl_runs_status ON etl_runs(status);

-- ============================================================================
-- Triggers: Auto-update updated_at timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON funding_opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_awards_updated_at
    BEFORE UPDATE ON nsf_awards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chunks_updated_at
    BEFORE UPDATE ON opportunity_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function: Search opportunities with full-text search
CREATE OR REPLACE FUNCTION search_opportunities(
    search_query TEXT,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS SETOF funding_opportunities AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM funding_opportunities
    WHERE
        to_tsvector('english', title || ' ' || COALESCE(summary, '')) @@ plainto_tsquery('english', search_query)
    ORDER BY
        ts_rank(to_tsvector('english', title || ' ' || COALESCE(summary, '')), plainto_tsquery('english', search_query)) DESC,
        close_date ASC NULLS LAST
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Get opportunities closing soon (within N days)
CREATE OR REPLACE FUNCTION get_closing_soon_opportunities(days INTEGER DEFAULT 7)
RETURNS SETOF funding_opportunities AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM funding_opportunities
    WHERE
        close_date IS NOT NULL
        AND close_date >= CURRENT_DATE
        AND close_date <= CURRENT_DATE + (days || ' days')::INTERVAL
    ORDER BY close_date ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================
COMMENT ON TABLE funding_opportunities IS 'Federal funding opportunities from NSF and Grants.gov';
COMMENT ON TABLE nsf_awards IS 'Historical NSF award data for analysis and recommendations';
COMMENT ON TABLE opportunity_chunks IS 'Text chunks for vector embeddings and RAG search';
COMMENT ON TABLE opportunity_updates IS 'Audit trail of opportunity changes';
COMMENT ON TABLE etl_runs IS 'ETL execution logs for monitoring and debugging';

COMMENT ON COLUMN funding_opportunities.content_hash IS 'MD5 hash of title+summary for change detection';
COMMENT ON COLUMN funding_opportunities.deadline_status IS 'Computed field: open | closing_soon | closed | unknown';
COMMENT ON COLUMN opportunity_chunks.chunk_type IS 'Semantic category: summary | eligibility | requirements | timeline';

-- ============================================================================
-- Initial Data (Optional)
-- ============================================================================

-- Insert initial ETL run record
INSERT INTO etl_runs (run_date, status)
VALUES (NOW(), 'started')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Grants and Permissions (for Supabase Auth)
-- ============================================================================

-- Grant read access to authenticated users
-- (Uncomment when Supabase Auth is configured)
-- ALTER TABLE funding_opportunities ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY "Allow authenticated users to read opportunities"
--     ON funding_opportunities
--     FOR SELECT
--     TO authenticated
--     USING (true);
--
-- CREATE POLICY "Allow authenticated users to read awards"
--     ON nsf_awards
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- ============================================================================
-- End of Migration 001
-- ============================================================================
