"""Transform NSF awards API payloads."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from ..models import Award

logger = logging.getLogger(__name__)


class AwardTransformer:
    """Normalize NSF awards into internal schema."""

    def __init__(self, *, settings) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    def transform(self, payload: Dict[str, Any]) -> List[Award]:
        records: List[Award] = []
        raw_awards = payload.get("response", {}).get("award", [])
        for item in raw_awards:
            normalized = self._normalize(item)
            records.append(Award(**normalized))
        logger.info("Transformed NSF awards", extra={"count": len(records)})
        return records

    def _normalize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        pi_names = []
        for key in ("piFirstName", "piMidName", "piLastName"):
            value = item.get(key)
            if value:
                pi_names.append(value.strip())

        program_codes = item.get("programElementCode") or []
        if isinstance(program_codes, str):
            program_codes = [program_codes]

        return {
            "id": str(item.get("id")),
            "title": item.get("title", ""),
            "pi_names": pi_names,
            "organization_code": item.get("agency", {}).get("code"),
            "directorate": item.get("dirCode"),
            "division": item.get("divisionDirectorate"),
            "start_date": self._parse_date(item.get("startDate")),
            "end_date": self._parse_date(item.get("expDate")),
            "award_amount": self._parse_float(item.get("awardAmount")),
            "abstract": item.get("abstractText"),
            "program_reference_codes": program_codes,
            "publication_date": self._parse_date(item.get("date")),
        }

    def _parse_date(self, value: Any):  # type: ignore[no-untyped-def]
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            logger.warning("Failed to parse award date", extra={"value": value})
            return None

    def _parse_float(self, value: Any):  # type: ignore[no-untyped-def]
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            logger.warning("Failed to parse award amount", extra={"value": value})
            return None
