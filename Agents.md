# Agents

## Data Ingestion Agent
- **Scope**: Execute `apps.etl.pipeline`, monitor source availability, manage schema drift.
- **Inputs**: NSF Award Search API, Grants.gov XML snapshot, environment configuration (`.env`).
- **Outputs**: Normalized JSON snapshots, Supabase upserts, vector store updates.
- **Playbooks**:
  - `scripts/run_etl.sh` for manual runs
  - Future GitHub Actions workflow for scheduled ingestion

## Knowledge Retrieval Agent
- **Scope**: Serve question answering and semantic search once API layer is implemented.
- **Inputs**: Supabase/Postgres metadata, Pinecone/Chroma embeddings.
- **Outputs**: Ranked funding opportunities, synthesized answers with sources.
- **Status**: Not yet implemented; planned under `services/api/`.

## Notification Agent
- **Scope**: Deliver alert digests across Slack/email, enforce throttling, and track engagement.
- **Inputs**: User preferences, opportunity data changes, analytics signals.
- **Outputs**: Notification payloads, delivery metrics, feedback loops.
- **Status**: Pending implementation in `services/alerts/`.

## UX Research & Insights Agent
- **Scope**: Coordinate user interviews, process feedback, update product requirements.
- **Inputs**: Research sessions, surveys, PostHog analytics.
- **Outputs**: Updated `docs/product/` artifacts, backlog reprioritization, onboarding copy.
- **Status**: Framework defined; needs resourcing for execution.

## Collaboration Guidelines
- Log hand-offs in `docs/requests/YYYY-MM-DD.md`.
- Surface blockers in backlog document and update release notes before tagging new versions.
- Use feature flags to gate unfinished work; agents communicate via GitHub issues and shared Notion workspace.
