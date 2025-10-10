# Database Migrations

## Overview
This directory contains SQL migration scripts for the GovFunding Chatbot Supabase/PostgreSQL database. Migrations are versioned numerically and must be applied sequentially.

## Migration Naming Convention
```
{version}_{description}.sql
```

Examples:
- `001_initial_schema.sql`
- `002_add_vector_extension.sql`
- `003_add_user_preferences.sql`

Each migration should have a corresponding rollback script:
- `001_initial_schema_rollback.sql`

---

## Current Migrations

| Version | File | Description | Date | Status |
|---------|------|-------------|------|--------|
| 001 | `001_initial_schema.sql` | Create core tables (opportunities, awards, chunks, etc.) | 2025-10-10 | ✅ Ready |
| 002 | `002_add_vector_extension.sql` | Add pgvector for embeddings (Planned) | TBD | 🔜 Pending |
| 003 | `003_add_user_tables.sql` | User preferences, saved searches (Planned) | TBD | 🔜 Pending |

---

## How to Apply Migrations

### Option 1: Supabase Dashboard (Recommended for MVP)
1. Log in to [Supabase Dashboard](https://app.supabase.com)
2. Navigate to **SQL Editor**
3. Copy contents of `001_initial_schema.sql`
4. Click **Run** to execute
5. Verify tables created in **Table Editor**

### Option 2: Supabase CLI (For Production)
```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref <your-project-ref>

# Apply migration
supabase db push
```

### Option 3: Direct PostgreSQL Connection
```bash
# Using psql
psql -h db.<your-project>.supabase.co \
     -U postgres \
     -d postgres \
     -f 001_initial_schema.sql

# Or via connection string
psql "postgresql://postgres:[password]@db.<project>.supabase.co:5432/postgres" \
     -f 001_initial_schema.sql
```

---

## Migration Checklist

Before applying each migration:
- [ ] Review SQL for syntax errors
- [ ] Check for breaking changes
- [ ] Backup existing data (if applicable)
- [ ] Test in local/staging environment
- [ ] Document any manual steps required
- [ ] Update this README with migration status

After applying:
- [ ] Verify tables/columns created
- [ ] Test queries against new schema
- [ ] Update application code to match schema
- [ ] Update data models in `apps/etl/models.py`

---

## Rollback Procedure

If a migration fails or needs to be reverted:

```bash
# Apply rollback script
psql -h db.<your-project>.supabase.co \
     -U postgres \
     -d postgres \
     -f 001_initial_schema_rollback.sql
```

**⚠️ WARNING:** Rollback scripts DROP tables and DELETE data. Always backup first.

---

## Schema Validation

After applying migrations, verify schema integrity:

```sql
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check constraints
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    contype AS constraint_type
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace;
```

---

## Future Migrations (Planned)

### 002: Vector Extension (Week 2)
**Purpose:** Enable pgvector for storing embeddings
```sql
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE opportunity_chunks
ADD COLUMN embedding vector(1536); -- OpenAI ada-002 dimension

CREATE INDEX idx_chunks_embedding
ON opportunity_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Decision:** Use pgvector OR Pinecone (not both). Currently planned for Pinecone external service.

### 003: User Tables (Week 3)
**Purpose:** Store user preferences and saved searches
```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    research_areas TEXT[],
    institution TEXT,
    notification_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE saved_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    opportunity_id TEXT NOT NULL REFERENCES funding_opportunities(opportunity_id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, opportunity_id)
);
```

### 004: Alert Rules (Week 4)
**Purpose:** User-defined alert configurations
```sql
CREATE TABLE alert_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    rule_name TEXT NOT NULL,
    filters JSONB NOT NULL, -- Stored search criteria
    notification_channels TEXT[] DEFAULT '{"email"}',
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Testing Migrations

### Local Testing with Docker
```bash
# Start local Postgres
docker run --name govfunding-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15

# Apply migration
psql -h localhost -U postgres -d postgres -f 001_initial_schema.sql

# Test queries
psql -h localhost -U postgres -d postgres -c "SELECT * FROM funding_opportunities LIMIT 5;"
```

### Seed Test Data
```sql
-- Insert sample opportunity
INSERT INTO funding_opportunities (
    opportunity_id,
    title,
    agency_code,
    agency_name,
    summary,
    award_floor,
    award_ceiling,
    post_date,
    close_date
) VALUES (
    'NSF-23-612',
    'Advancing Informal STEM Learning (AISL)',
    'NSF',
    'National Science Foundation',
    'The Advancing Informal STEM Learning program seeks to advance new approaches...',
    50000,
    500000,
    '2025-03-15',
    '2025-04-15'
);

-- Verify insert
SELECT * FROM funding_opportunities WHERE opportunity_id = 'NSF-23-612';
```

---

## Troubleshooting

### Issue: "Permission denied for relation..."
**Solution:** Ensure you're using the `postgres` superuser or service_role key.

### Issue: "Extension 'uuid-ossp' does not exist"
**Solution:** Run `CREATE EXTENSION "uuid-ossp";` manually first.

### Issue: "Index creation taking too long"
**Solution:**
- For large datasets, create indexes AFTER bulk insert
- Use `CREATE INDEX CONCURRENTLY` to avoid locking

### Issue: "Rollback script fails with foreign key constraints"
**Solution:** Drop tables in reverse dependency order (already handled in rollback script).

---

## Resources

- [Supabase Database Docs](https://supabase.com/docs/guides/database)
- [PostgreSQL 15 Documentation](https://www.postgresql.org/docs/15/)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [pgvector Extension](https://github.com/pgvector/pgvector)

---

**Last Updated:** 2025-10-10
**Maintainer:** GovFunding Core Team
**Review Cycle:** Before each new migration
