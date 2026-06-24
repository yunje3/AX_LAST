from __future__ import annotations

import streamlit as st

from src import auth, storage

st.set_page_config(page_title="TeamSync Manager", page_icon="TS", layout="wide")
storage.init_state()

st.title("TeamSync Manager")
st.caption("DB 없이 JSON 샘플 데이터와 세션 상태로 동작하는 팀 프로젝트/일정/채팅 관리 테스트 버전")

if auth.current_user():
    user = auth.current_user()
    with st.sidebar:
        st.write(f"**{user['name']}**")
        st.caption(f"{user['role']} / team_id={user['team_id']}")
        if st.button("로그아웃", use_container_width=True):
            auth.logout()
            st.rerun()
        if st.button("샘플 데이터 초기화", use_container_width=True):
            storage.reset_demo_data()
            st.success("샘플 데이터로 초기화했습니다.")
            st.rerun()

    st.success("로그인되었습니다. 왼쪽 Pages 메뉴에서 대시보드, 프로젝트, 일정, 채팅, 관리자 화면을 선택하세요.")
    st.info("테스트 버전은 세션 내 변경사항만 유지됩니다. Streamlit Cloud에서 앱이 재시작되면 data/*.json 샘플 데이터로 돌아갑니다.")

    cols = st.columns(4)
    cols[0].metric("팀", len(storage.list_rows("teams")))
    cols[1].metric("프로젝트", len(storage.list_rows("projects")))
    cols[2].metric("일정", len(storage.list_rows("schedules")))
    cols[3].metric("채팅 메시지", len(storage.list_rows("chat_messages")))
else:
    st.subheader("로그인")
    st.write("아래 샘플 계정으로 테스트할 수 있습니다.")
    st.dataframe(
        [
            {"권한": "Admin", "이메일": "admin@teamsync.test", "비밀번호": "admin123"},
            {"권한": "Manager", "이메일": "manager@teamsync.test", "비밀번호": "manager123"},
            {"권한": "Member", "이메일": "member@teamsync.test", "비밀번호": "member123"},
        ],
        use_container_width=True,
        hide_index=True,
    )
    with st.form("login_form"):
        email = st.text_input("이메일", value="admin@teamsync.test")
        password = st.text_input("비밀번호", value="admin123", type="password")
        submitted = st.form_submit_button("로그인", use_container_width=True)
    if submitted:
        if auth.login(email, password):
            st.rerun()
        else:
            st.error("이메일 또는 비밀번호가 올바르지 않거나 비활성 계정입니다.")
