from __future__ import annotations

import streamlit as st

from src import auth, storage

st.set_page_config(page_title="관리자", layout="wide")
user = auth.require_login()

st.title("관리자")

if user.get("role") != "Admin":
    st.error("Admin 권한이 필요합니다.")
    st.stop()

teams = storage.list_rows("teams")
users = storage.list_rows("users")
team_map = storage.team_map()

team_tab, user_tab, data_tab = st.tabs(["팀 관리", "사용자 관리", "테스트 데이터"])

with team_tab:
    st.subheader("팀 목록")
    st.dataframe(teams, use_container_width=True, hide_index=True)
    with st.form("team_create"):
        name = st.text_input("팀명")
        description = st.text_area("설명")
        if st.form_submit_button("팀 생성") and name:
            storage.add_row("teams", {"name": name, "description": description})
            st.success("팀을 생성했습니다.")
            st.rerun()

with user_tab:
    st.subheader("사용자 목록")
    st.dataframe([
        {
            "ID": row["id"],
            "이름": row["name"],
            "이메일": row["email"],
            "권한": row["role"],
            "팀": team_map.get(row.get("team_id"), "-"),
            "직책": row.get("position"),
            "활성": row.get("is_active", True),
        }
        for row in users
    ], use_container_width=True, hide_index=True)

    with st.form("user_create"):
        name = st.text_input("이름")
        email = st.text_input("이메일")
        password = st.text_input("테스트 비밀번호", type="password")
        role = st.selectbox("권한", ["Admin", "Manager", "Member"], index=2)
        team_id = st.selectbox("팀", [row["id"] for row in teams], format_func=lambda value: team_map.get(value, str(value)))
        position = st.text_input("직책")
        submitted = st.form_submit_button("사용자 생성")
    if submitted and name and email and password:
        storage.add_row("users", {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "team_id": team_id,
            "position": position,
            "is_active": True,
        })
        st.success("사용자를 생성했습니다.")
        st.rerun()

    if users:
        with st.expander("사용자 권한/상태 수정", expanded=False):
            user_id = st.selectbox("사용자", [row["id"] for row in users], format_func=lambda value: next(row["name"] for row in users if row["id"] == value))
            target = next(row for row in users if row["id"] == user_id)
            with st.form("user_update"):
                role = st.selectbox("권한", ["Admin", "Manager", "Member"], index=["Admin", "Manager", "Member"].index(target["role"]))
                team_id = st.selectbox("팀", [row["id"] for row in teams], index=[row["id"] for row in teams].index(target["team_id"]), format_func=lambda value: team_map.get(value, str(value)))
                is_active = st.checkbox("활성", value=target.get("is_active", True))
                if st.form_submit_button("수정"):
                    storage.update_row("users", user_id, {"role": role, "team_id": team_id, "is_active": is_active})
                    if auth.current_user() and auth.current_user()["id"] == user_id:
                        st.session_state.current_user.update({"role": role, "team_id": team_id})
                    st.success("사용자를 수정했습니다.")
                    st.rerun()

with data_tab:
    st.subheader("세션 데이터 상태")
    cols = st.columns(4)
    cols[0].metric("사용자", len(storage.list_rows("users")))
    cols[1].metric("프로젝트", len(storage.list_rows("projects")))
    cols[2].metric("일정", len(storage.list_rows("schedules")))
    cols[3].metric("채팅", len(storage.list_rows("chat_messages")))
    st.warning("테스트 버전의 변경사항은 현재 세션에만 저장됩니다.")
    if st.button("모든 샘플 데이터 초기화", use_container_width=True):
        storage.reset_demo_data()
        st.success("초기화했습니다.")
        st.rerun()
