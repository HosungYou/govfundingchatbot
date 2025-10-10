"""Time-related helpers."""

from __future__ import annotations

from datetime import datetime


def format_date(value: datetime) -> str:
    """Format datetime to NSF API date string (MM/DD/YYYY)."""

    return value.strftime("%m/%d/%Y")
