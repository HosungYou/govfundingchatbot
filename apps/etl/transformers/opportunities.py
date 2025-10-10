"""Transform Grants.gov XML into normalized opportunity records."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from lxml import etree

from apps.etl.models import Opportunity

logger = logging.getLogger(__name__)


class OpportunityTransformer:
    """Transform XML snapshot into normalized opportunities."""

    def __init__(self, *, settings) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    def transform(self, xml_path: Path) -> List[Opportunity]:
        logger.info("Parsing opportunity XML", extra={"path": str(xml_path)})

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(str(xml_path), parser).getroot()
        records: List[Opportunity] = []

        ns = {"g": "http://apply.grants.gov/system/OpportunityDetail-V1.0"}
        for node in root.findall("g:OpportunitySynopsisDetail_1_0", ns):
            payload = {
                "opportunityId": self._text(node, "g:OpportunityID", ns),
                "title": self._text(node, "g:OpportunityTitle", ns) or "",
                "agency_code": self._text(node, "g:AgencyCode", ns),
                "agency_name": self._text(node, "g:AgencyName", ns),
                "summary": self._text(node, "g:Description", ns),
                "cfda_numbers": self._list(node, "g:CFDANumbers", ns),
                "funding_category": self._text(node, "g:OpportunityCategory", ns),
                "instrument_types": self._list(node, "g:FundingInstrumentType", ns),
                "award_floor": self._float(node, "g:AwardFloor", ns),
                "award_ceiling": self._float(node, "g:AwardCeiling", ns),
                "estimated_total": self._float(node, "g:EstimatedTotalProgramFunding", ns),
                "post_date": self._date(node, "g:PostDate", ns),
                "close_date": self._date(node, "g:CloseDate", ns),
                "archive_date": self._date(node, "g:ArchiveDate", ns),
                "eligibility_text": self._text(node, "g:AdditionalInformationOnEligibility", ns),
                "cost_sharing_required": self._bool(node, "g:CostSharingOrMatchingRequirement", ns),
            }
            records.append(Opportunity(**payload))

        logger.info("Transformed opportunities", extra={"count": len(records)})
        return records

    def _text(self, node, xpath: str, ns):  # type: ignore[no-untyped-def]
        element = node.find(xpath, ns)
        if element is None or element.text is None:
            return None
        return element.text.strip()

    def _list(self, node, xpath: str, ns):  # type: ignore[no-untyped-def]
        elements = node.findall(xpath, ns)
        return [e.text.strip() for e in elements if e is not None and e.text]

    def _float(self, node, xpath: str, ns):  # type: ignore[no-untyped-def]
        text = self._text(node, xpath, ns)
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            logger.warning("Failed to parse float", extra={"value": text, "xpath": xpath})
            return None

    def _date(self, node, xpath: str, ns):  # type: ignore[no-untyped-def]
        text = self._text(node, xpath, ns)
        if not text:
            return None
        try:
            # Grants.gov uses MMDDYYYY format
            return datetime.strptime(text, "%m%d%Y").date()
        except ValueError:
            logger.warning("Failed to parse date", extra={"value": text, "xpath": xpath})
            return None

    def _bool(self, node, xpath: str, ns):  # type: ignore[no-untyped-def]
        text = self._text(node, xpath, ns)
        if not text:
            return None
        normalized = text.lower()
        if normalized in {"yes", "y", "true"}:
            return True
        if normalized in {"no", "n", "false"}:
            return False
        return None
