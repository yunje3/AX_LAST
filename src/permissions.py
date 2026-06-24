from __future__ import annotations

from src import storage


def can_access_team(user: dict, team_id: int | None) -> bool:
    if user.get("role") == "Admin":
        return True
    return team_id == user.get("team_id")


def accessible_users(user: dict) -> list[dict]:
    rows = [row for row in storage.list_rows("users") if row.get("is_active", True)]
    if user.get("role") == "Admin":
        return rows
    return [row for row in rows if row.get("team_id") == user.get("team_id")]


def accessible_projects(user: dict) -> list[dict]:
    projects = storage.list_rows("projects")
    if user.get("role") == "Admin":
        return projects
    if user.get("role") == "Manager":
        return [row for row in projects if row.get("team_id") == user.get("team_id")]
    member_project_ids = {
        row["project_id"]
        for row in storage.list_rows("project_members")
        if row.get("user_id") == user.get("id")
    }
    return [row for row in projects if row.get("id") in member_project_ids]


def accessible_schedules(user: dict) -> list[dict]:
    schedules = storage.list_rows("schedules")
    if user.get("role") == "Admin":
        return schedules
    if user.get("role") == "Manager":
        return [row for row in schedules if row.get("team_id") == user.get("team_id")]
    return [row for row in schedules if row.get("user_id") == user.get("id")]


def accessible_rooms(user: dict) -> list[dict]:
    rooms = storage.list_rows("chat_rooms")
    if user.get("role") == "Admin":
        return rooms
    projects = {row["id"] for row in accessible_projects(user)}
    return [
        row
        for row in rooms
        if row.get("team_id") == user.get("team_id")
        or (row.get("project_id") in projects)
    ]


def can_manage_project(user: dict, project: dict | None = None) -> bool:
    if user.get("role") == "Admin":
        return True
    if user.get("role") != "Manager":
        return False
    if project is None:
        return True
    return project.get("team_id") == user.get("team_id")
