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
│       ├── config.py
│       ├── models.py
│       ├── pipeline.py
│       ├── sources/
│       ├── transformers/
│       ├── utils/
│       └── writers/
├── docs/
│   ├── architecture/
│   ├── backlog/
│   ├── product/
│   └── requests/
├── release-notes/
│   ├── README.md
│   └── v1.0.0.md
├── scripts/
│   └── run_etl.sh
├── .env.sample
├── .gitignore
└── pyproject.toml
```

## Directory Descriptions
- `apps/`: Source code for runtime applications and services.
  - `apps/etl/`: Python ETL package powering NSF data ingestion and normalization.
- `docs/`: Structured documentation grouped by topic (architecture, backlog, product specs, request logs).
- `release-notes/`: Versioned release documentation following WFED119 guidelines.
- `scripts/`: Developer and CI helpers for running pipelines and maintenance tasks.
- Root files (`Agents.md`, `PROJECT_STRUCTURE.md`, `README.md`): orientation, team responsibilities, and high-level overview.

## Planned Additions
- `services/api/`: FastAPI search and retrieval service (Phase 2).
- `services/alerts/`: Notification workers (Phase 4).
- `apps/web/`: Next.js frontend deployed to Vercel (Phase 3).
- `infra/`: Infrastructure-as-code, Supabase migrations, deployment scripts.
