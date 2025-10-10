"""Persist normalized data to local filesystem snapshots."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ..config import Settings
from ..models import Award, Opportunity


class LocalWriter:
    """Write normalized outputs to structured JSON files."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    def write_awards(self, awards: Iterable[Award]) -> Path:
        target_dir = self._target_dir("awards")
        filename = f"awards-normalized-{datetime.utcnow():%Y%m%dT%H%M%S}.json"
        path = target_dir / filename
        payload = [award.model_dump(by_alias=True) for award in awards]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def write_opportunities(self, opportunities: Iterable[Opportunity]) -> Path:
        target_dir = self._target_dir("opportunities")
        filename = f"opportunities-normalized-{datetime.utcnow():%Y%m%dT%H%M%S}.json"
        path = target_dir / filename
        payload = [opportunity.model_dump(by_alias=True) for opportunity in opportunities]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _target_dir(self, slug: str) -> Path:
        target = self.settings.local_data_dir / "normalized" / slug
        target.mkdir(parents=True, exist_ok=True)
        return target
