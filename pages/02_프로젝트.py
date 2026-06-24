from __future__ import annotations

from datetime import date

import streamlit as st

from src import auth, permissions, services, storage

st.set_page_config(page_title="프로젝트", layout="wide")
user = auth.require_login()

st.title("프로젝트")
st.caption("프로젝트와 하위 태스크를 관리합니다.")

projects = permissions.accessible_projects(user)
teams = storage.team_map()
users = storage.user_map()

status_filter = st.multiselect("상태 필터", ["예정", "진행 중", "보류", "완료", "취소"], default=[])
keyword = st.text_input("프로젝트명 검색")
filtered = projects
if status_filter:
    filtered = [row for row in filtered if row.get("status") in status_filter]
if keyword:
    filtered = [row for row in filtered if keyword.lower() in row.get("name", "").lower()]

st.subheader("프로젝트 목록")
st.dataframe([
    {
        "ID": row["id"],
        "프로젝트": row["name"],
        "팀": teams.get(row.get("team_id"), "-"),
        "담당자": users.get(row.get("owner_id"), "-"),
        "상태": row["status"],
        "시작일": row["start_date"],
        "마감일": row["due_date"],
    }
    for row in filtered
], use_container_width=True, hide_index=True)

if auth.is_manager_or_admin():
    with st.expander("프로젝트 생성", expanded=False):
        with st.form("project_create"):
            name = st.text_input("프로젝트명")
            description = st.text_area("설명")
            team_options = storage.team_map()
            allowed_team_ids = list(team_options) if user["role"] == "Admin" else [user["team_id"]]
            team_id = st.selectbox("팀", allowed_team_ids, format_func=lambda value: team_options.get(value, str(value)))
            owner_candidates = [row for row in storage.list_rows("users") if row.get("team_id") == team_id and row.get("is_active", True)]
            owner_id = st.selectbox("담당자", [row["id"] for row in owner_candidates], format_func=lambda value: users.get(value, str(value)))
            status = st.selectbox("상태", ["예정", "진행 중", "보류", "완료", "취소"], index=1)
            start_date = st.date_input("시작일", value=date.today())
            due_date = st.date_input("마감일", value=date.today())
            submitted = st.form_submit_button("생성")
        if submitted and name:
            project = storage.add_row("projects", {
                "team_id": team_id,
                "name": name,
                "description": description,
                "owner_id": owner_id,
                "status": status,
                "start_date": start_date.isoformat(),
                "due_date": due_date.isoformat(),
            })
            storage.add_project_member(project["id"], owner_id, "PM")
            st.success("프로젝트를 생성했습니다.")
            st.rerun()

if filtered:
    st.subheader("프로젝트 상세 및 태스크")
    selected_id = st.selectbox("프로젝트 선택", [row["id"] for row in filtered], format_func=lambda value: next(row["name"] for row in filtered if row["id"] == value))
    project = next(row for row in filtered if row["id"] == selected_id)
    st.write(f"**설명:** {project.get('description', '')}")

    if permissions.can_manage_project(user, project):
        with st.form("project_update"):
            status = st.selectbox("상태 변경", ["예정", "진행 중", "보류", "완료", "취소"], index=["예정", "진행 중", "보류", "완료", "취소"].index(project["status"]))
            due_date = st.date_input("마감일 변경", value=date.fromisoformat(project["due_date"]))
            if st.form_submit_button("프로젝트 수정"):
                storage.update_row("projects", selected_id, {"status": status, "due_date": due_date.isoformat()})
                st.success("프로젝트를 수정했습니다.")
                st.rerun()

    task_rows = [row for row in storage.list_rows("tasks") if row.get("project_id") == selected_id]
    st.dataframe([
        {
            "ID": row["id"],
            "태스크": row["title"],
            "담당자": services.get_user_name(row.get("assignee_id")),
            "상태": row["status"],
            "우선순위": row["priority"],
            "진행률": row["progress"],
            "마감일": row["due_date"],
        }
        for row in task_rows
    ], use_container_width=True, hide_index=True)

    with st.expander("태스크 추가/수정", expanded=False):
        project_users = [row for row in storage.list_rows("users") if row.get("team_id") == project.get("team_id") and row.get("is_active", True)]
        with st.form("task_create"):
            title = st.text_input("태스크명")
            description = st.text_area("태스크 설명")
            assignee_id = st.selectbox("담당자", [row["id"] for row in project_users], format_func=lambda value: users.get(value, str(value)))
            task_status = st.selectbox("상태", ["할 일", "진행 중", "검토 중", "완료"])
            priority = st.selectbox("우선순위", ["낮음", "보통", "높음", "긴급"], index=1)
            due = st.date_input("마감일", value=date.today())
            progress = st.slider("진행률", 0, 100, 0)
            if st.form_submit_button("태스크 추가") and title:
                storage.add_row("tasks", {
                    "project_id": selected_id,
                    "assignee_id": assignee_id,
                    "title": title,
                    "description": description,
                    "status": task_status,
                    "priority": priority,
                    "due_date": due.isoformat(),
                    "progress": progress,
                })
                storage.add_project_member(selected_id, assignee_id)
                st.success("태스크를 추가했습니다.")
                st.rerun()

        if task_rows:
            with st.form("task_update"):
                task_id = st.selectbox("수정할 태스크", [row["id"] for row in task_rows], format_func=lambda value: next(row["title"] for row in task_rows if row["id"] == value))
                target = next(row for row in task_rows if row["id"] == task_id)
                new_status = st.selectbox("새 상태", ["할 일", "진행 중", "검토 중", "완료"], index=["할 일", "진행 중", "검토 중", "완료"].index(target["status"]))
                new_progress = st.slider("새 진행률", 0, 100, int(target.get("progress", 0)))
                if st.form_submit_button("태스크 수정"):
                    storage.update_row("tasks", task_id, {"status": new_status, "progress": new_progress})
                    st.success("태스크를 수정했습니다.")
                    st.rerun()
