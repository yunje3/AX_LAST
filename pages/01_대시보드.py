from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src import auth, permissions, services, storage, utils

st.set_page_config(page_title="대시보드", layout="wide")
user = auth.require_login()

st.title("대시보드")
st.caption("프로젝트, 태스크, 일정, 채팅 현황 요약")

projects = permissions.accessible_projects(user)
schedules = permissions.accessible_schedules(user)
tasks = storage.list_rows("tasks")
project_ids = {row["id"] for row in projects}
visible_tasks = [row for row in tasks if row.get("project_id") in project_ids]
if user["role"] == "Member":
    visible_tasks = [row for row in visible_tasks if row.get("assignee_id") == user["id"]]

col1, col2, col3, col4 = st.columns(4)
col1.metric("프로젝트", len(projects))
col2.metric("진행 중", sum(1 for row in projects if row.get("status") == "진행 중"))
col3.metric("내/팀 태스크", len(visible_tasks))
col4.metric("일정", len(schedules))

left, right = st.columns([1.2, 1])
with left:
    st.subheader("프로젝트 상태")
    if projects:
        df = pd.DataFrame(projects)
        chart_df = df.groupby("status", as_index=False).size()
        fig = px.bar(chart_df, x="status", y="size", labels={"size": "개수", "status": "상태"}, text="size")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("조회 가능한 프로젝트가 없습니다.")

with right:
    st.subheader("마감 임박 태스크")
    upcoming = []
    today = date.today()
    for task in visible_tasks:
        due = utils.parse_date(task.get("due_date"))
        if due and today <= due <= today + timedelta(days=14) and task.get("status") != "완료":
            upcoming.append({
                "태스크": task["title"],
                "프로젝트": services.get_project_name(task.get("project_id")),
                "담당자": services.get_user_name(task.get("assignee_id")),
                "마감일": task.get("due_date"),
                "상태": task.get("status"),
            })
    st.dataframe(upcoming, use_container_width=True, hide_index=True)

st.subheader("이번 주 일정")
week_start = date.today() - timedelta(days=date.today().weekday())
week_end = week_start + timedelta(days=6)
week_rows = []
for row in schedules:
    start = utils.parse_date(row.get("start_at"))
    if start and week_start <= start <= week_end:
        week_rows.append({
            "일자": row["start_at"][:10],
            "유형": row["schedule_type"],
            "제목": row["title"],
            "사용자": services.get_user_name(row.get("user_id")),
            "프로젝트": services.get_project_name(row.get("project_id")),
        })
st.dataframe(week_rows, use_container_width=True, hide_index=True)

st.subheader("최근 채팅")
rooms = {row["id"]: row for row in permissions.accessible_rooms(user)}
messages = [row for row in storage.list_rows("chat_messages") if row.get("room_id") in rooms]
messages = sorted(messages, key=lambda row: row.get("created_at", ""), reverse=True)[:5]
st.dataframe([
    {
        "시간": utils.format_datetime(row.get("created_at")),
        "채팅방": rooms[row["room_id"]]["name"],
        "작성자": services.get_user_name(row.get("user_id")),
        "메시지": row.get("message"),
    }
    for row in messages
], use_container_width=True, hide_index=True)
