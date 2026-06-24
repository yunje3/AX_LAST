from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TABLES = [
    "teams",
    "users",
    "projects",
    "project_members",
    "tasks",
    "schedules",
    "chat_rooms",
    "chat_messages",
]


def _load_json(table: str) -> list[dict[str, Any]]:
    path = DATA_DIR / f"{table}.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def init_state() -> None:
    if st.session_state.get("data_loaded"):
        return
    for table in TABLES:
        st.session_state[table] = _load_json(table)
    st.session_state.data_loaded = True


def reset_demo_data() -> None:
    for table in TABLES:
        st.session_state[table] = _load_json(table)
    st.session_state.data_loaded = True


def list_rows(table: str) -> list[dict[str, Any]]:
    init_state()
    return deepcopy(st.session_state.get(table, []))


def get_row(table: str, row_id: int) -> dict[str, Any] | None:
    for row in list_rows(table):
        if row.get("id") == row_id:
            return row
    return None


def next_id(table: str) -> int:
    rows = st.session_state.get(table, [])
    return max([int(row.get("id", 0)) for row in rows] or [0]) + 1


def add_row(table: str, values: dict[str, Any]) -> dict[str, Any]:
    init_state()
    row = deepcopy(values)
    if "id" not in row:
        row["id"] = next_id(table)
    row.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    st.session_state[table].append(row)
    return deepcopy(row)


def update_row(table: str, row_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
    init_state()
    for index, row in enumerate(st.session_state[table]):
        if row.get("id") == row_id:
            updated = {**row, **values}
            st.session_state[table][index] = updated
            return deepcopy(updated)
    return None


def delete_row(table: str, row_id: int) -> None:
    init_state()
    st.session_state[table] = [row for row in st.session_state[table] if row.get("id") != row_id]


def add_project_member(project_id: int, user_id: int, role: str = "Member") -> None:
    init_state()
    exists = any(
        row.get("project_id") == project_id and row.get("user_id") == user_id
        for row in st.session_state.project_members
    )
    if not exists:
        st.session_state.project_members.append({"project_id": project_id, "user_id": user_id, "role": role})


def user_map() -> dict[int, str]:
    return {row["id"]: row["name"] for row in list_rows("users")}


def team_map() -> dict[int, str]:
    return {row["id"]: row["name"] for row in list_rows("teams")}


def project_map() -> dict[int, str]:
    return {row["id"]: row["name"] for row in list_rows("projects")}

