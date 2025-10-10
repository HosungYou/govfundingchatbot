# Project Structure

```
.
├── Agents.md
├── PROJECT_STRUCTURE.md
├── README.md
├── apps/
│   ├── __init__.py
│   └── etl/
│       ├── __init__.py
│       ├── config.py               # Environment settings with Supabase support
│       ├── models.py                # Pydantic models for Opportunity/Award
│       ├── pipeline.py              # Main ETL orchestration
│       ├── sources/
│       │   ├── nsf_awards.py       # NSF API extractor (with retry logic)
│       │   └── grants_xml.py       # Grants.gov ZIP extractor
│       ├── transformers/
│       │   ├── awards.py           # NSF award normalization
│       │   └── opportunities.py    # Grants.gov XML parser
│       ├── utils/
│       │   └── time.py             # Date formatting helpers
│       └── writers/
│           ├── local.py            # JSON snapshot writer (backup)
│           └── supabase.py         # Supabase/PostgreSQL writer (NEW)
├── docs/
│   ├── architecture/
│   │   ├── deployment-strategy.md  # Vercel + Render deployment plan (NEW)
│   │   └── system-overview.md
│   ├── backlog/
│   │   └── unimplemented-features.md
│   ├── design/
│   │   └── ui-layout-specification.md  # Pixel-perfect UI layouts (NEW)
│   ├── product/
│   │   ├── data-pipeline.md
│   │   ├── roadmap.md
│   │   ├── ui-mvp.md
│   │   └── user-research.md
│   └── requests/
│       └── 2025-10-10.md
├── infra/                           # NEW: Infrastructure as code
│   └── migrations/
│       ├── README.md                # Migration guide
│       ├── 001_initial_schema.sql  # Core tables DDL
│       └── 001_initial_schema_rollback.sql
├── release-notes/
│   ├── README.md
│   ├── v1.0.0.md                    # Updated with release date
│   └── v1.1.0.md                    # Updated with version comparison
├── scripts/
│   └── run_etl.sh
├── .env.sample                      # Updated with Supabase vars
├── .gitignore
└── pyproject.toml                   # Updated with supabase + tenacity deps
```

## Directory Descriptions

### Core Application (`apps/`)
- **`apps/etl/`**: Production-ready ETL pipeline
  - **Sources**: Data extraction with exponential backoff retry (3 attempts)
  - **Transformers**: Pydantic-validated data normalization
  - **Writers**: Dual output (local JSON + Supabase upsert with change detection)
  - **Config**: Centralized settings via `pydantic-settings`

### Documentation (`docs/`)
- **`architecture/`**: System diagrams, deployment strategy, API specs
- **`design/`**: UI/UX specifications with pixel-level layouts
- **`product/`**: Product requirements, roadmaps, research plans
- **`backlog/`**: Unimplemented features tracker
- **`requests/`**: Daily stakeholder request logs

### Infrastructure (`infra/`)
- **`migrations/`**: Versioned SQL migrations for Supabase
  - `001`: Core tables (opportunities, awards, chunks, etl_runs)
  - Future: pgvector extension, user tables, alert rules

### Scripts (`scripts/`)
- **`run_etl.sh`**: Shell wrapper for `poetry run python -m apps.etl.pipeline`

## Implemented vs Planned

### ✅ Implemented (v1.0.0 - v1.1.0)
- ETL pipeline with retry logic
- Supabase writer with change detection
- Database schema migrations
- Deployment strategy documentation
- UI design specification

### 🔜 Next Phase (v1.2.0)
- Supabase row-level security (RLS) policies
- Next.js frontend scaffolding
- Server Actions for data access
- RAG Edge Functions

### 🔮 Future (v2.0.0+)
- `services/api/`: FastAPI search service (Optional - may not be needed)
- `services/alerts/`: Email/Slack notification workers
- `apps/web/`: Full Next.js dashboard

## Key Design Decisions

1. **No FastAPI Layer**: Next.js Server Actions directly query Supabase (simplified architecture)
2. **Vercel + Render Split**: Frontend on Vercel, ETL on Render (free tiers)
3. **Dual Writers**: Always write to local JSON (backup) + Supabase (primary)
4. **Change Detection**: MD5 hashing prevents unnecessary database updates
5. **Retry Strategy**: Exponential backoff on all HTTP operations (tenacity library)
