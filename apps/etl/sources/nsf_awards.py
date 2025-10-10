"""Extractor for NSF awards API."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from apps.etl.config import Settings
from apps.etl.utils.time import format_date

logger = logging.getLogger(__name__)


class NSFAwardsExtractor:
    """Fetch NSF awards data within a date window."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    def fetch(self, *, window_start: datetime, window_end: datetime) -> Dict[str, Any]:
        """
        Fetch NSF awards with retry logic.

        Args:
            window_start: Start of date range
            window_end: End of date range

        Returns:
            Raw API response payload
        """
        params = {
            "dateStart": format_date(window_start),
            "dateEnd": format_date(window_end),
            "printFields": "id,title,piFirstName,piLastName,startDate,expDate,fundsObligatedAmt,abstractText,awardee,agency",
        }
        logger.info("Fetching NSF awards", extra=params)

        headers = {
            "User-Agent": "GovFundingChatbot/1.0 (+https://github.com/HosungYou/govfundingchatbot)"
        }
        response = httpx.get(
            str(self.settings.nsf_awards_api),
            params=params,
            headers=headers,
            timeout=60,
            follow_redirects=True
        )

        # Log response details for debugging
        if response.status_code != 200:
            logger.error(
                f"NSF API returned {response.status_code}: {response.text[:500]}"
            )

        response.raise_for_status()
        payload = response.json()
        self._persist_raw(payload, window_start, window_end)
        return payload

    def _persist_raw(self, payload: Dict[str, Any], window_start: datetime, window_end: datetime) -> None:
        data_dir = self.settings.local_data_dir / "raw" / "nsf_awards"
        data_dir.mkdir(parents=True, exist_ok=True)
        filename = f"awards-{window_start:%Y%m%d}-{window_end:%Y%m%d}.json"
        path = data_dir / filename
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved NSF awards payload", extra={"path": str(path)})
