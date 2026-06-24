from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value[:10]).date()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def as_dataframe(rows: list[dict[str, Any]], empty_columns: list[str] | None = None) -> pd.DataFrame:
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame(columns=empty_columns or [])


def format_datetime(value: str | None) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def status_badge(status: str) -> str:
    colors = {
        "예정": "#64748b",
        "진행 중": "#2563eb",
        "보류": "#d97706",
        "완료": "#059669",
        "취소": "#dc2626",
        "할 일": "#64748b",
        "검토 중": "#7c3aed",
    }
    color = colors.get(status, "#64748b")
    return f"<span style='color:white;background:{color};padding:3px 8px;border-radius:999px;font-size:12px'>{status}</span>"
