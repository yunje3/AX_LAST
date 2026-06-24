from __future__ import annotations

from src import storage


def get_team_name(team_id: int | None) -> str:
    if team_id is None:
        return "-"
    return storage.team_map().get(team_id, "-")


def get_user_name(user_id: int | None) -> str:
    if user_id is None:
        return "-"
    return storage.user_map().get(user_id, "-")


def get_project_name(project_id: int | None) -> str:
    if project_id is None:
        return "-"
    return storage.project_map().get(project_id, "-")
