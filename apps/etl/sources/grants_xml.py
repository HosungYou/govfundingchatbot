"""Extractor for Grants.gov opportunity XML snapshot."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from ..config import Settings

logger = logging.getLogger(__name__)


class GrantsXMLExtractor:
    """Download Grants.gov snapshot and return local file path."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    def fetch(self) -> Path:
        logger.info("Downloading Grants.gov snapshot", extra={"url": str(self.settings.grants_xml_url)})

        response = httpx.get(str(self.settings.grants_xml_url), timeout=60)
        response.raise_for_status()

        data_dir = self.settings.local_data_dir / "raw" / "nsf_opportunities"
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"opportunities-{datetime.utcnow():%Y%m%dT%H%M%S}.xml"
        snapshot_path = data_dir / filename
        snapshot_path.write_bytes(response.content)
        logger.info("Saved Grants.gov snapshot", extra={"path": str(snapshot_path)})
        return snapshot_path
