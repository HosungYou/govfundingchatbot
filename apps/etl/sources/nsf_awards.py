"""Extractor for NSF awards API."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict

import httpx

from ..config import Settings
from ..utils.time import format_date

logger = logging.getLogger(__name__)


class NSFAwardsExtractor:
    """Fetch NSF awards data within a date window."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    def fetch(self, *, window_start: datetime, window_end: datetime) -> Dict[str, Any]:
        params = {
            "dateStart": format_date(window_start),
            "dateEnd": format_date(window_end),
            "printFields": "id,title,piFirstName,piLastName,startDate,expDate,awardAmount,abstractText,awardeeName,agency,dirCode,divisionDirectorate,programElementCode",
        }
        logger.info("Fetching NSF awards", extra=params)

        response = httpx.get(str(self.settings.nsf_awards_api), params=params, timeout=30)
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
