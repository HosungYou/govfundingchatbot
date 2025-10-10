-- Rollback Migration: 001_initial_schema_rollback.sql
-- Description: Rollback script for 001_initial_schema.sql
-- WARNING: This will DROP all tables and data. Use with caution.

-- Drop functions first
DROP FUNCTION IF EXISTS search_opportunities(TEXT, INTEGER, INTEGER);
DROP FUNCTION IF EXISTS get_closing_soon_opportunities(INTEGER);
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse order (respecting foreign keys)
DROP TABLE IF EXISTS etl_runs CASCADE;
DROP TABLE IF EXISTS opportunity_updates CASCADE;
DROP TABLE IF EXISTS opportunity_chunks CASCADE;
DROP TABLE IF EXISTS nsf_awards CASCADE;
DROP TABLE IF EXISTS funding_opportunities CASCADE;

-- Drop extensions (only if not used by other schemas)
-- Uncomment if you're sure no other tables use these
-- DROP EXTENSION IF EXISTS "pg_trgm";
-- DROP EXTENSION IF EXISTS "uuid-ossp";
