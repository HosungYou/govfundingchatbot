# Data Pipeline Specification

## Objectives
- Deliver daily normalized NSF funding opportunity and award data with deterministic updates.
- Minimize third-party lock-in while keeping Pinecone compatibility for future scaling.
- Provide incremental change feeds that downstream services (Next.js app, alert service) can consume without reprocessing the full dataset.

## Source Inventory
- NSF Award Search API (`https://api.nsf.gov/services/v1/awards.json`)
  - Filters: `dateStart`, `dateEnd`, `agency`, `program`.
  - cadence: daily at 05:00 UTC, with `dateStart` set to previous run timestamp.
- NSF Funding Opportunity RSS/XML (Grants.gov `OpportunitySynopsisDetail_1_0`).
  - Pull full XML snapshot (`temp_latest.zip`) daily; derive diff against previous snapshot.
- Supplemental reference tables
  - NSF Organization Directory (CSV) → provides division, directorate hierarchy.
  - CFDA registry (JSON) → friendly names for CFDA codes.

## Run Orchestration
- GitHub Actions workflow (`.github/workflows/etl.yml`).
  - Triggers: cron `0 5 * * *` and manual dispatch.
  - Steps: checkout repo → setup Python via Poetry → run `scripts/run_etl.sh`.
  - Artifacts: raw payloads archived per run, summary log uploaded to build artifacts for audit.

## Data Lake Layout (S3-compatible bucket)
```
s3://govfunding-data/
  raw/
    nsf_awards/YYYY/MM/DD/awards-YYYYMMDD.json
    nsf_opportunities/YYYY/MM/DD/opportunities-YYYYMMDD.xml
  staging/
    nsf_awards/YYYYMMDD.parquet
    nsf_opportunities/YYYYMMDD.parquet
  curated/
    nsf_awards_latest.parquet
    nsf_opportunities_latest.parquet
  hash/
    opportunity_chunks/YYYYMMDD.json
```

## Normalized Warehouse Schema (Supabase/Postgres)
`funding_opportunities`
- `opportunity_id` (PK, grants.gov ID)
- `title`, `summary`, `agency_code`, `agency_name`
- `cfda_numbers` (array)
- `funding_category` (enum), `instrument_types` (array)
- `award_floor`, `award_ceiling`, `estimated_total`
- `post_date`, `close_date`, `archive_date`
- `eligibility_text`, `cost_sharing_required`
- `last_synced_at`

`nsf_awards`
- `nsf_award_id` (PK), `award_title`, `pi_names`
- `organization_code`, `directorate`, `division`
- `start_date`, `end_date`, `award_amount`
- `abstract_text`, `program_reference_codes`
- `publication_date`, `last_synced_at`

`opportunity_topics`
- `opportunity_id` (FK), `topic` (text), `source` (model/manual)

`opportunity_updates`
- `opportunity_id` (FK)
- `update_type` (`created` | `modified` | `archived`)
- `update_payload` (JSONB), `updated_at`

`opportunity_chunks`
- `chunk_id` (PK), `opportunity_id`, `chunk_index`
- `content` (text), `content_hash`
- `embedding` (vector or separate table depending on backend)
- `updated_at`

## ETL Stages
1. **Extract**
   - `apps/etl/nsf_awards_ingest.py`: call NSF API with incremental window, store response to `data/raw/` and S3.
   - `apps/etl/opportunities_ingest.py`: download XML, parse with `lxml`, save raw XML + intermediate JSON.
   - Persist run metadata to `apps/etl/run_state.json` for next-window computation.

2. **Transform**
   - Convert raw payloads to normalized dictionaries using Pydantic models (`apps/etl/models.py`).
   - Standardize dates, currency numeric types, dedupe contacts.
   - Generate derived fields: `deadline_status` (open/closing_soon/closed), `award_midpoint`.
   - Chunk opportunity descriptions via `RecursiveCharacterTextSplitter` with metadata.

3. **Load**
   - Upsert normalized rows into Postgres using `COPY` + staging tables (`load_temp_nsf_awards` etc.).
   - Compute change detection by comparing `md5(content)`; only update Pinecone/Chroma for changed hashes.
   - Publish summary message to queue (later: `alerts` service) containing diff counts.

## Monitoring & Logging
- Structured logging with Python `structlog`, output JSON to stdout for GitHub Actions capture.
- Supabase table `etl_runs` storing run id, duration, counts, success flag.
- Slack webhook (optional) for fail/success notifications with key metrics.

## Local Development
- `.env` template stored in `config/.env.sample`.
- Developer command: `poetry run python -m apps.etl.pipeline --date 2025-04-05`.
- Use `docker-compose` (future) to run Postgres+Chroma locally.

## Next Steps
1. Implement `apps/etl/config.py` with settings management via `pydantic-settings`.
2. Build `apps/etl/nsf_awards_ingest.py` skeleton and fixture tests.
3. Define Supabase schema migration scripts under `migrations/`.
4. Draft GitHub Actions workflow and run-local script.
