from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from src import auth, permissions, services, storage, utils

st.set_page_config(page_title="일정", layout="wide")
user = auth.require_login()

st.title("일정")
st.caption("근무, 재택근무, 출장, 휴가, 외근 일정을 관리합니다.")

schedules = permissions.accessible_schedules(user)
type_options = ["근무", "재택근무", "출장", "휴가", "반차", "외근", "교육", "기타"]
selected_types = st.multiselect("일정 유형", type_options, default=[])
start_filter, end_filter = st.columns(2)
with start_filter:
    start_date = st.date_input("조회 시작일", value=date.today().replace(day=1))
with end_filter:
    end_date = st.date_input("조회 종료일", value=date.today())

filtered = []
for row in schedules:
    row_date = utils.parse_date(row.get("start_at"))
    if not row_date:
        continue
    if selected_types and row.get("schedule_type") not in selected_types:
        continue
    if start_date <= row_date <= end_date:
        filtered.append(row)

st.subheader("일정 목록")
st.dataframe([
    {
        "ID": row["id"],
        "일시": utils.format_datetime(row.get("start_at")),
        "유형": row["schedule_type"],
        "제목": row["title"],
        "사용자": services.get_user_name(row.get("user_id")),
        "팀": services.get_team_name(row.get("team_id")),
        "프로젝트": services.get_project_name(row.get("project_id")),
        "상태": row["approval_status"],
    }
    for row in filtered
], use_container_width=True, hide_index=True)

left, right = st.columns([1, 1])
with left:
    st.subheader("일정 등록")
    with st.form("schedule_create"):
        users = permissions.accessible_users(user)
        if user["role"] == "Member":
            users = [row for row in users if row["id"] == user["id"]]
        user_id = st.selectbox("사용자", [row["id"] for row in users], format_func=lambda value: services.get_user_name(value))
        target_user = next(row for row in users if row["id"] == user_id)
        project_options = [None] + [row["id"] for row in permissions.accessible_projects(user)]
        project_id = st.selectbox("관련 프로젝트", project_options, format_func=lambda value: "없음" if value is None else services.get_project_name(value))
        schedule_type = st.selectbox("유형", type_options)
        title = st.text_input("제목")
        description = st.text_area("설명")
        day = st.date_input("일자", value=date.today())
        all_day = st.checkbox("종일")
        if all_day:
            start_at = datetime.combine(day, time(9, 0))
            end_at = datetime.combine(day, time(18, 0))
        else:
            c1, c2 = st.columns(2)
            with c1:
                start_time = st.time_input("시작 시간", value=time(9, 0))
            with c2:
                end_time = st.time_input("종료 시간", value=time(18, 0))
            start_at = datetime.combine(day, start_time)
            end_at = datetime.combine(day, end_time)
        submitted = st.form_submit_button("일정 등록")
    if submitted and title:
        storage.add_row("schedules", {
            "user_id": user_id,
            "team_id": target_user["team_id"],
            "project_id": project_id,
            "schedule_type": schedule_type,
            "title": title,
            "description": description,
            "start_at": start_at.isoformat(timespec="minutes"),
            "end_at": end_at.isoformat(timespec="minutes"),
            "is_all_day": all_day,
            "approval_status": "등록",
        })
        st.success("일정을 등록했습니다.")
        st.rerun()

with right:
    st.subheader("휴가/출장/외근 현황")
    away = [row for row in filtered if row.get("schedule_type") in {"휴가", "반차", "출장", "외근"}]
    st.dataframe([
        {
            "일자": row["start_at"][:10],
            "유형": row["schedule_type"],
            "사용자": services.get_user_name(row.get("user_id")),
            "제목": row["title"],
        }
        for row in away
    ], use_container_width=True, hide_index=True)

if filtered:
    with st.expander("일정 수정/삭제", expanded=False):
        editable = filtered if user["role"] in {"Admin", "Manager"} else [row for row in filtered if row.get("user_id") == user["id"]]
        if editable:
            schedule_id = st.selectbox("대상 일정", [row["id"] for row in editable], format_func=lambda value: next(row["title"] for row in editable if row["id"] == value))
            target = next(row for row in editable if row["id"] == schedule_id)
            with st.form("schedule_update"):
                title = st.text_input("제목 수정", value=target["title"])
                schedule_type = st.selectbox("유형 수정", type_options, index=type_options.index(target["schedule_type"]))
                approval_status = st.selectbox("상태", ["등록", "승인 대기", "승인", "반려"], index=["등록", "승인 대기", "승인", "반려"].index(target["approval_status"]))
                c1, c2 = st.columns(2)
                save = c1.form_submit_button("수정")
                delete = c2.form_submit_button("삭제")
            if save:
                storage.update_row("schedules", schedule_id, {"title": title, "schedule_type": schedule_type, "approval_status": approval_status})
                st.success("일정을 수정했습니다.")
                st.rerun()
            if delete:
                storage.delete_row("schedules", schedule_id)
                st.success("일정을 삭제했습니다.")
                st.rerun()
        else:
            st.info("수정 가능한 일정이 없습니다.")
