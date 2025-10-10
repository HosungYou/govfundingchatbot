# Execution Roadmap

## Phase 0 – Repository Setup (Week 0)
- Initialize git repository, connect to GitHub remote `HosungYou/govfundingchatbot`.
- Add project README with vision, architecture diagram, and contribution guide.
- Create `.env.sample`, `pyproject.toml`, and `poetry.lock` baseline.

## Phase 1 – Data Foundations (Week 1-2)
- Build NSF awards and Grants.gov opportunity extractors with incremental sync.
- Implement Pydantic models and transformation layer.
- Provision Supabase project, apply schema migrations, seed reference tables.
- Set up Chroma vector store for local development + Pinecone integration toggle.

## Phase 2 – API & Services (Week 3-4)
- Develop FastAPI service for search + RAG endpoints (later deploy as Vercel serverless). 
- Integrate authentication (Supabase Auth) and rate limiting.
- Implement alert scheduler stub (Async cron) publishing to notification queue.

## Phase 3 – Frontend MVP (Week 5-6)
- Scaffold Next.js app, implement dashboard/search/detail routes.
- Hook UI to API endpoints, ensure responsive layouts and skeleton states.
- Integrate PostHog analytics, error monitoring, and feature flag system.

## Phase 4 – Growth Features & QA (Week 7-8)
- Build notification delivery (Email & Slack) tied to alert preferences.
- Add bookmarking, shared workspace, and .ics export.
- Perform accessibility, performance, and cross-browser QA.
- Conduct private beta with initial cohort, gather feedback, iterate.

## Deliverables Checklist
- [ ] GitHub Actions ETL workflow operational.
- [ ] Daily data snapshots stored and retrievable.
- [ ] Supabase/Postgres schema migrated.
- [ ] REST/RAG endpoints tested.
- [ ] Next.js MVP deployed to Vercel preview.
- [ ] Alert system delivering notifications to seed users.
- [ ] Research findings incorporated into backlog.
