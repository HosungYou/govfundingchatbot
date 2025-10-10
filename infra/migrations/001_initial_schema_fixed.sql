-- Migration: 001_initial_schema_fixed.sql
-- Description: Supabase-compatible version (fixes generated column syntax)
-- Author: GovFunding Core Team
-- Date: 2025-10-10

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Table: funding_opportunities (FIXED)
-- ============================================================================
CREATE TABLE IF NOT EXISTS funding_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    agency_code TEXT,
    agency_name TEXT,
    cfda_numbers TEXT[] DEFAULT '{}',
    funding_category TEXT,
    instrument_types TEXT[] DEFAULT '{}',
    award_floor NUMERIC(15, 2),
    award_ceiling NUMERIC(15, 2),
    estimated_total NUMERIC(15, 2),
    post_date DATE,
    close_date DATE,
    archive_date DATE,
    eligibility_text TEXT,
    cost_sharing_required BOOLEAN DEFAULT false,
    content_hash TEXT,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Computed fields (removed GENERATED - will use trigger instead)
    deadline_status TEXT,
    award_midpoint NUMERIC(15, 2),

    CONSTRAINT check_award_range CHECK (
        award_floor IS NULL OR award_ceiling IS NULL OR award_floor <= award_ceiling
    ),
    CONSTRAINT check_close_date_after_post CHECK (
        post_date IS NULL OR close_date IS NULL OR close_date >= post_date
    )
);

-- Trigger to auto-compute deadline_status and award_midpoint
CREATE OR REPLACE FUNCTION update_computed_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Compute deadline_status
    NEW.deadline_status := CASE
        WHEN NEW.close_date IS NULL THEN 'unknown'
        WHEN NEW.close_date < CURRENT_DATE THEN 'closed'
        WHEN NEW.close_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'closing_soon'
        ELSE 'open'
    END;

    -- Compute award_midpoint
    IF NEW.award_floor IS NOT NULL AND NEW.award_ceiling IS NOT NULL THEN
        NEW.award_midpoint := (NEW.award_floor + NEW.award_ceiling) / 2;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER compute_opportunity_fields
    BEFORE INSERT OR UPDATE ON funding_opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_computed_fields();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_opportunities_agency ON funding_opportunities(agency_code);
CREATE INDEX IF NOT EXISTS idx_opportunities_close_date ON funding_opportunities(close_date);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline_status ON funding_opportunities(deadline_status);
CREATE INDEX IF NOT EXISTS idx_opportunities_post_date ON funding_opportunities(post_date DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_funding_category ON funding_opportunities(funding_category);
CREATE INDEX IF NOT EXISTS idx_opportunities_last_synced ON funding_opportunities(last_synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_title_search ON funding_opportunities USING GIN (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_opportunities_summary_search ON funding_opportunities USING GIN (to_tsvector('english', COALESCE(summary, '')));
CREATE INDEX IF NOT EXISTS idx_opportunities_agency_close_date ON funding_opportunities(agency_code, close_date);

-- ============================================================================
-- Table: nsf_awards
-- ============================================================================
CREATE TABLE IF NOT EXISTS nsf_awards (
    nsf_award_id TEXT PRIMARY KEY,
    award_title TEXT NOT NULL,
    pi_names TEXT[] DEFAULT '{}',
    organization_code TEXT,
    organization_name TEXT,
    directorate TEXT,
    division TEXT,
    start_date DATE,
    end_date DATE,
    award_amount NUMERIC(15, 2),
    abstract_text TEXT,
    program_reference_codes TEXT[] DEFAULT '{}',
    publication_date DATE,
    content_hash TEXT,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT check_award_dates CHECK (
        start_date IS NULL OR end_date IS NULL OR end_date >= start_date
    )
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_awards_directorate ON nsf_awards(directorate);
CREATE INDEX IF NOT EXISTS idx_awards_division ON nsf_awards(division);
CREATE INDEX IF NOT EXISTS idx_awards_start_date ON nsf_awards(start_date DESC);
CREATE INDEX IF NOT EXISTS idx_awards_award_amount ON nsf_awards(award_amount DESC);
CREATE INDEX IF NOT EXISTS idx_awards_publication_date ON nsf_awards(publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_awards_title_search ON nsf_awards USING GIN (to_tsvector('english', award_title));
CREATE INDEX IF NOT EXISTS idx_awards_abstract_search ON nsf_awards USING GIN (to_tsvector('english', COALESCE(abstract_text, '')));

-- ============================================================================
-- Table: opportunity_chunks
-- ============================================================================
CREATE TABLE IF NOT EXISTS opportunity_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT NOT NULL REFERENCES funding_opportunities(opportunity_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    chunk_type TEXT DEFAULT 'summary',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_opportunity_chunk UNIQUE (opportunity_id, chunk_index),
    CONSTRAINT check_chunk_index CHECK (chunk_index >= 0)
);

CREATE INDEX IF NOT EXISTS idx_chunks_opportunity_id ON opportunity_chunks(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_chunks_content_hash ON opportunity_chunks(content_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_type ON opportunity_chunks(chunk_type);

-- ============================================================================
-- Table: opportunity_updates
-- ============================================================================
CREATE TABLE IF NOT EXISTS opportunity_updates (
    update_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT NOT NULL REFERENCES funding_opportunities(opportunity_id) ON DELETE CASCADE,
    update_type TEXT NOT NULL CHECK (update_type IN ('created', 'modified', 'archived')),
    update_payload JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_updates_opportunity_id ON opportunity_updates(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_updates_updated_at ON opportunity_updates(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_updates_update_type ON opportunity_updates(update_type);

-- ============================================================================
-- Table: etl_runs
-- ============================================================================
CREATE TABLE IF NOT EXISTS etl_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed', 'partial')),
    opportunities_extracted INTEGER DEFAULT 0,
    opportunities_created INTEGER DEFAULT 0,
    opportunities_updated INTEGER DEFAULT 0,
    awards_extracted INTEGER DEFAULT 0,
    awards_created INTEGER DEFAULT 0,
    awards_updated INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    error_message TEXT,
    error_trace TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_run_date ON etl_runs(run_date DESC);
CREATE INDEX IF NOT EXISTS idx_etl_runs_status ON etl_runs(status);

-- ============================================================================
-- Triggers: Auto-update updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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
-- Comments
-- ============================================================================
COMMENT ON TABLE funding_opportunities IS 'Federal funding opportunities from NSF and Grants.gov';
COMMENT ON TABLE nsf_awards IS 'Historical NSF award data';
COMMENT ON TABLE opportunity_chunks IS 'Text chunks for RAG vector search';
COMMENT ON TABLE opportunity_updates IS 'Audit trail of opportunity changes';
COMMENT ON TABLE etl_runs IS 'ETL execution logs';

-- ============================================================================
-- Initial Data
-- ============================================================================
INSERT INTO etl_runs (run_date, status)
VALUES (NOW(), 'started')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Success Message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Migration 001 completed successfully!';
    RAISE NOTICE 'Tables created: funding_opportunities, nsf_awards, opportunity_chunks, opportunity_updates, etl_runs';
    RAISE NOTICE 'Next step: Run ETL pipeline to populate data';
END $$;
