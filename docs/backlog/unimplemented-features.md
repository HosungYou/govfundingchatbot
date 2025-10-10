# Unimplemented Features & Workstreams

## Application Services
- FastAPI search/RAG service with Supabase + Pinecone integration
- Alert scheduler service delivering Slack, email, and calendar digests
- Next.js dashboard (`apps/web`) with authentication, filters, and analytics

## Data & Infrastructure
- Supabase/Postgres schema migrations (`infra/migrations`)
- Incremental load diffing and retry/backoff logic in ETL
- Vector store synchronization with change detection (hash → upsert)
- Terraform or Pulumi stack defining Vercel, Supabase, and monitoring resources

## Product & UX
- Onboarding survey for interest areas and notification preferences
- Insight visualizations (funding trends, award analytics)
- Collaboration features (shared workspaces, comments, exports)

## Quality & Operations
- Automated test suite (pytest) covering transformers and writers
- GitHub Actions workflows for ETL cron, linting, and deployment
- Observability integrations (Sentry, Logflare, PostHog)

## Documentation
- API reference for planned endpoints under `docs/architecture/api.md`
- Deployment runbooks for ops handover
- Pricing/packaging guide once monetization strategy defined
