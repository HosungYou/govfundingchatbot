# GovFunding Chatbot

GovFunding Chatbot aggregates NSF funding opportunities and awards, normalizes the data, and powers a retrieval-augmented assistant plus proactive alerting features. The repository now contains the foundational ETL pipeline, product documentation, and release history required to ship the MVP.

## Getting Started
1. Install Poetry: `pipx install poetry`
2. Install dependencies: `poetry install`
3. Copy `.env.sample` → `.env` and provide the necessary credentials (NSF API, Grants.gov snapshot URL, Supabase, Pinecone/Chroma, storage targets).
4. Run the ETL pipeline locally:
   ```bash
   scripts/run_etl.sh
   ```
   The command executes `python -m apps.etl.pipeline`, producing normalized JSON snapshots under `data/` (gitignored).

## Repository Tour
- `apps/etl/`: Modular ETL package (extractors, transformers, writers, configuration).
- `docs/product/`: Product strategy artifacts (data pipeline spec, UI blueprint, user research plan, roadmap).
- `docs/architecture/`: System overview diagrams and future service layouts.
- `docs/backlog/`: Outstanding workstreams and unimplemented features.
- `docs/requests/`: Daily request logs capturing stakeholder asks and fulfillment status.
- `release-notes/`: Versioned release documentation (currently v1.0.0).
- `scripts/`: Developer utilities (`run_etl.sh`).
- `Agents.md`: Roles and responsibilities for AI/automation agents supporting the project.
- `PROJECT_STRUCTURE.md`: Snapshot of the repo layout with planned additions.

## Roadmap Snapshot
Key milestones are documented in `docs/product/roadmap.md` and complemented by the architecture plan in `docs/architecture/system-overview.md`. Upcoming work includes:
- Shipping the FastAPI-based search & RAG service (`services/api`).
- Building the Next.js dashboard deployed on Vercel (`apps/web`).
- Implementing the alert scheduler for Slack/email digests (`services/alerts`).
- Hardening ETL with Supabase migrations, retries, and automated testing.

## Release History
- **v1.0.0** — Repository bootstrap with modular ETL, planning docs, and release note scaffolding. See `release-notes/v1.0.0.md` for details.

## Contributing
- Format/lint using `ruff` and `black` (configure in future commits).
- Document major changes in release notes before tagging a version.
- Update request logs (`docs/requests/`) whenever new stakeholder asks arrive.

Questions, feedback, or blockers should be logged via GitHub issues and reflected in the backlog documentation.
