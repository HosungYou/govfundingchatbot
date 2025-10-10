"""Orchestrates the end-to-end ETL process."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import Settings, get_settings
from .sources.nsf_awards import NSFAwardsExtractor
from .sources.grants_xml import GrantsXMLExtractor
from .transformers.opportunities import OpportunityTransformer
from .transformers.awards import AwardTransformer
from .writers.local import LocalWriter
from .writers.supabase import SupabaseWriter

logger = logging.getLogger(__name__)


def run_pipeline(run_date: Optional[datetime] = None, *, settings: Optional[Settings] = None) -> None:
    """Run extract, transform, load cycle for NSF data."""

    settings = settings or get_settings()
    run_date = run_date or datetime.utcnow()

    logger.info("Starting ETL run", extra={"run_date": run_date.isoformat()})

    try:
        # Extract
        window_days = settings.nsf_awards_window_days
        window_start = run_date - timedelta(days=window_days)

        awards_extractor = NSFAwardsExtractor(settings=settings)
        opportunities_extractor = GrantsXMLExtractor(settings=settings)

        logger.info("Extracting data from sources")
        awards_raw = awards_extractor.fetch(window_start=window_start, window_end=run_date)
        opportunities_raw = opportunities_extractor.fetch()

        # Transform
        logger.info("Transforming data")
        awards_normalized = AwardTransformer(settings=settings).transform(awards_raw)
        opportunities_normalized = OpportunityTransformer(settings=settings).transform(opportunities_raw)

        # Load - Always write to local for backup
        local_writer = LocalWriter(settings=settings)
        local_writer.write_awards(awards_normalized)
        local_writer.write_opportunities(opportunities_normalized)

        # Load - Write to Supabase if configured
        opp_stats = {}
        award_stats = {}
        if settings.database_url and settings.supabase_service_key:
            logger.info("Writing to Supabase")
            supabase_writer = SupabaseWriter(settings=settings)
            opp_stats = supabase_writer.write_opportunities(opportunities_normalized)
            award_stats = supabase_writer.write_awards(awards_normalized)
            supabase_writer.log_etl_run("success", opp_stats, award_stats)
        else:
            logger.warning("Supabase not configured, skipping database write")

        logger.info(
            "ETL run completed successfully",
            extra={
                "awards_count": len(awards_normalized),
                "opportunities_count": len(opportunities_normalized),
                "supabase_opp_stats": opp_stats,
                "supabase_award_stats": award_stats,
            },
        )

    except Exception as e:
        logger.error("ETL run failed", extra={"error": str(e)}, exc_info=True)

        # Log failure to Supabase if configured
        if settings and settings.database_url and settings.supabase_service_key:
            try:
                supabase_writer = SupabaseWriter(settings=settings)
                supabase_writer.log_etl_run("failed")
            except Exception:
                pass  # Ignore errors in error logging

        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
