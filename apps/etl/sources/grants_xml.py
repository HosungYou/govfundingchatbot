"""Extractor for Grants.gov opportunity XML snapshot."""

from __future__ import annotations

import logging
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from apps.etl.config import Settings

logger = logging.getLogger(__name__)


class GrantsXMLExtractor:
    """Download Grants.gov snapshot ZIP and extract XML."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    def fetch(self) -> Path:
        """
        Download Grants.gov ZIP snapshot and extract XML.

        Returns:
            Path to extracted XML file
        """
        logger.info("Downloading Grants.gov snapshot", extra={"url": str(self.settings.grants_xml_url)})

        # Download ZIP file with retry logic
        response = httpx.get(str(self.settings.grants_xml_url), timeout=120, follow_redirects=True)
        response.raise_for_status()

        data_dir = self.settings.local_data_dir / "raw" / "nsf_opportunities"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Handle ZIP extraction
        if response.headers.get("content-type", "").startswith("application/zip") or self._is_zip_content(
            response.content
        ):
            logger.info("Extracting ZIP archive")
            return self._extract_zip(response.content, data_dir)
        else:
            # Fallback: treat as XML directly
            logger.warning("Response is not a ZIP file, treating as raw XML")
            return self._save_raw_xml(response.content, data_dir)

    def _is_zip_content(self, content: bytes) -> bool:
        """Check if content starts with ZIP magic number."""
        return content[:4] == b"PK\x03\x04"

    def _extract_zip(self, zip_content: bytes, target_dir: Path) -> Path:
        """Extract XML from ZIP archive."""
        with zipfile.ZipFile(BytesIO(zip_content)) as z:
            # Find XML file in ZIP (usually named GrantsDBExtract*.xml)
            xml_files = [f for f in z.namelist() if f.endswith(".xml")]

            if not xml_files:
                raise ValueError("No XML files found in ZIP archive")

            # Extract first XML file
            xml_filename = xml_files[0]
            logger.info("Extracting XML file", extra={"filename": xml_filename})

            extracted_path = target_dir / f"opportunities-{datetime.utcnow():%Y%m%dT%H%M%S}.xml"
            with z.open(xml_filename) as source, extracted_path.open("wb") as target:
                target.write(source.read())

            logger.info("Saved extracted XML", extra={"path": str(extracted_path)})
            return extracted_path

    def _save_raw_xml(self, content: bytes, target_dir: Path) -> Path:
        """Save raw XML content (fallback when not a ZIP)."""
        filename = f"opportunities-{datetime.utcnow():%Y%m%dT%H%M%S}.xml"
        snapshot_path = target_dir / filename
        snapshot_path.write_bytes(content)
        logger.info("Saved raw XML snapshot", extra={"path": str(snapshot_path)})
        return snapshot_path
