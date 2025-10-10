"""Pydantic models describing normalized records."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Opportunity(BaseModel):
    opportunity_id: str = Field(..., alias="opportunityId")
    title: str
    agency_code: Optional[str] = Field(default=None)
    agency_name: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    cfda_numbers: List[str] = Field(default_factory=list)
    funding_category: Optional[str] = Field(default=None)
    instrument_types: List[str] = Field(default_factory=list)
    award_floor: Optional[float] = None
    award_ceiling: Optional[float] = None
    estimated_total: Optional[float] = None
    post_date: Optional[date] = None
    close_date: Optional[date] = None
    archive_date: Optional[date] = None
    eligibility_text: Optional[str] = None
    cost_sharing_required: Optional[bool] = None
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)


class Award(BaseModel):
    nsf_award_id: str = Field(..., alias="id")
    award_title: str = Field(..., alias="title")
    pi_names: List[str] = Field(default_factory=list)
    organization_code: Optional[str] = None
    directorate: Optional[str] = None
    division: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    award_amount: Optional[float] = None
    abstract_text: Optional[str] = Field(default=None, alias="abstract")
    program_reference_codes: List[str] = Field(default_factory=list)
    publication_date: Optional[date] = None
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)


class Chunk(BaseModel):
    chunk_id: str
    opportunity_id: str
    chunk_index: int
    content: str
    content_hash: str
    embedding: Optional[list[float]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
