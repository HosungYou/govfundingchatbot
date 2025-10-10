"""Write normalized data to Supabase/PostgreSQL."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Iterable, List

from supabase import create_client, Client

from ..config import Settings
from ..models import Award, Opportunity

logger = logging.getLogger(__name__)


class SupabaseWriter:
    """Upsert normalized opportunities and awards into Supabase."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Lazy-load Supabase client."""
        if self._client is None:
            if not self.settings.database_url:
                raise ValueError("GOVFUNDING_DATABASE_URL not configured")
            if not self.settings.supabase_service_key:
                raise ValueError("GOVFUNDING_SUPABASE_SERVICE_KEY not configured")

            # Extract Supabase project URL from database_url
            # database_url format: postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
            # We need: https://[project].supabase.co
            db_url = str(self.settings.database_url)
            if "supabase.co" in db_url:
                project_ref = db_url.split("@db.")[1].split(".supabase.co")[0]
                supabase_url = f"https://{project_ref}.supabase.co"
            else:
                # Fallback: use direct URL if provided separately
                supabase_url = str(self.settings.database_url)

            self._client = create_client(supabase_url, self.settings.supabase_service_key)
            logger.info("Connected to Supabase", extra={"url": supabase_url})

        return self._client

    def write_opportunities(self, opportunities: Iterable[Opportunity]) -> dict:
        """
        Upsert opportunities with change detection.

        Returns:
            dict: Statistics with keys 'created', 'updated', 'unchanged'
        """
        opportunities_list = list(opportunities)
        logger.info("Writing opportunities to Supabase", extra={"count": len(opportunities_list)})

        stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": 0}

        for opp in opportunities_list:
            try:
                # Compute content hash for change detection
                content_for_hash = f"{opp.title}|{opp.summary or ''}"
                content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()

                # Check if opportunity exists
                existing = (
                    self.client.table("funding_opportunities")
                    .select("content_hash")
                    .eq("opportunity_id", opp.opportunity_id)
                    .maybe_single()
                    .execute()
                )

                # Prepare data payload
                data = {
                    "opportunity_id": opp.opportunity_id,
                    "title": opp.title,
                    "summary": opp.summary,
                    "agency_code": opp.agency_code,
                    "agency_name": opp.agency_name,
                    "cfda_numbers": opp.cfda_numbers,
                    "funding_category": opp.funding_category,
                    "instrument_types": opp.instrument_types,
                    "award_floor": float(opp.award_floor) if opp.award_floor else None,
                    "award_ceiling": float(opp.award_ceiling) if opp.award_ceiling else None,
                    "estimated_total": float(opp.estimated_total) if opp.estimated_total else None,
                    "post_date": opp.post_date.isoformat() if opp.post_date else None,
                    "close_date": opp.close_date.isoformat() if opp.close_date else None,
                    "archive_date": opp.archive_date.isoformat() if opp.archive_date else None,
                    "eligibility_text": opp.eligibility_text,
                    "cost_sharing_required": opp.cost_sharing_required,
                    "content_hash": content_hash,
                    "last_synced_at": datetime.utcnow().isoformat(),
                }

                if existing.data is None:
                    # Create new opportunity
                    self.client.table("funding_opportunities").insert(data).execute()
                    stats["created"] += 1
                    logger.debug("Created opportunity", extra={"id": opp.opportunity_id})

                    # Log update event
                    self._log_update(opp.opportunity_id, "created", {"title": opp.title})

                elif existing.data.get("content_hash") != content_hash:
                    # Update existing opportunity (content changed)
                    self.client.table("funding_opportunities").update(data).eq(
                        "opportunity_id", opp.opportunity_id
                    ).execute()
                    stats["updated"] += 1
                    logger.debug("Updated opportunity", extra={"id": opp.opportunity_id})

                    # Log update event
                    self._log_update(opp.opportunity_id, "modified", {"content_hash": content_hash})

                else:
                    # No changes detected
                    stats["unchanged"] += 1
                    logger.debug("Opportunity unchanged", extra={"id": opp.opportunity_id})

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Failed to write opportunity",
                    extra={"id": opp.opportunity_id, "error": str(e)},
                    exc_info=True,
                )

        logger.info("Opportunities write completed", extra=stats)
        return stats

    def write_awards(self, awards: Iterable[Award]) -> dict:
        """
        Upsert NSF awards with change detection.

        Returns:
            dict: Statistics with keys 'created', 'updated', 'unchanged'
        """
        awards_list = list(awards)
        logger.info("Writing awards to Supabase", extra={"count": len(awards_list)})

        stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": 0}

        for award in awards_list:
            try:
                # Compute content hash
                content_for_hash = f"{award.award_title}|{award.abstract_text or ''}"
                content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()

                # Check if award exists
                existing = (
                    self.client.table("nsf_awards")
                    .select("content_hash")
                    .eq("nsf_award_id", award.nsf_award_id)
                    .maybe_single()
                    .execute()
                )

                # Prepare data payload
                data = {
                    "nsf_award_id": award.nsf_award_id,
                    "award_title": award.award_title,
                    "pi_names": award.pi_names,
                    "organization_code": award.organization_code,
                    "directorate": award.directorate,
                    "division": award.division,
                    "start_date": award.start_date.isoformat() if award.start_date else None,
                    "end_date": award.end_date.isoformat() if award.end_date else None,
                    "award_amount": float(award.award_amount) if award.award_amount else None,
                    "abstract_text": award.abstract_text,
                    "program_reference_codes": award.program_reference_codes,
                    "publication_date": award.publication_date.isoformat()
                    if award.publication_date
                    else None,
                    "content_hash": content_hash,
                    "last_synced_at": datetime.utcnow().isoformat(),
                }

                if existing.data is None:
                    # Create new award
                    self.client.table("nsf_awards").insert(data).execute()
                    stats["created"] += 1
                    logger.debug("Created award", extra={"id": award.nsf_award_id})

                elif existing.data.get("content_hash") != content_hash:
                    # Update existing award
                    self.client.table("nsf_awards").update(data).eq(
                        "nsf_award_id", award.nsf_award_id
                    ).execute()
                    stats["updated"] += 1
                    logger.debug("Updated award", extra={"id": award.nsf_award_id})

                else:
                    # No changes
                    stats["unchanged"] += 1

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Failed to write award",
                    extra={"id": award.nsf_award_id, "error": str(e)},
                    exc_info=True,
                )

        logger.info("Awards write completed", extra=stats)
        return stats

    def _log_update(self, opportunity_id: str, update_type: str, payload: dict) -> None:
        """Log opportunity update event to opportunity_updates table."""
        try:
            self.client.table("opportunity_updates").insert(
                {
                    "opportunity_id": opportunity_id,
                    "update_type": update_type,
                    "update_payload": payload,
                }
            ).execute()
        except Exception as e:
            logger.warning("Failed to log update event", extra={"error": str(e)})

    def log_etl_run(
        self, status: str, opportunities_stats: dict | None = None, awards_stats: dict | None = None
    ) -> None:
        """
        Log ETL run to etl_runs table.

        Args:
            status: 'started' | 'success' | 'failed' | 'partial'
            opportunities_stats: Stats dict from write_opportunities()
            awards_stats: Stats dict from write_awards()
        """
        try:
            opp_stats = opportunities_stats or {}
            award_stats = awards_stats or {}

            self.client.table("etl_runs").insert(
                {
                    "status": status,
                    "opportunities_extracted": opp_stats.get("created", 0)
                    + opp_stats.get("updated", 0)
                    + opp_stats.get("unchanged", 0),
                    "opportunities_created": opp_stats.get("created", 0),
                    "opportunities_updated": opp_stats.get("updated", 0),
                    "awards_extracted": award_stats.get("created", 0)
                    + award_stats.get("updated", 0)
                    + award_stats.get("unchanged", 0),
                    "awards_created": award_stats.get("created", 0),
                    "awards_updated": award_stats.get("updated", 0),
                }
            ).execute()
            logger.info("Logged ETL run", extra={"status": status})
        except Exception as e:
            logger.error("Failed to log ETL run", extra={"error": str(e)}, exc_info=True)
