from __future__ import annotations

from datetime import datetime

import streamlit as st

from src import auth, permissions, services, storage, utils

st.set_page_config(page_title="채팅", layout="wide")
user = auth.require_login()

st.title("채팅")
st.caption("팀 또는 프로젝트별 메시지를 세션 데이터에 저장합니다.")

rooms = permissions.accessible_rooms(user)
if not rooms:
    st.info("접근 가능한 채팅방이 없습니다.")
    st.stop()

room_id = st.selectbox("채팅방", [row["id"] for row in rooms], format_func=lambda value: next(row["name"] for row in rooms if row["id"] == value))
room = next(row for row in rooms if row["id"] == room_id)

st.subheader(room["name"])
messages = [row for row in storage.list_rows("chat_messages") if row.get("room_id") == room_id]
messages = sorted(messages, key=lambda row: row.get("created_at", ""))

for message in messages[-50:]:
    with st.chat_message("user"):
        st.markdown(f"**{services.get_user_name(message.get('user_id'))}** · {utils.format_datetime(message.get('created_at'))}")
        st.write(message.get("message", ""))

with st.form("message_form", clear_on_submit=True):
    text = st.text_area("메시지", height=100)
    submitted = st.form_submit_button("전송", use_container_width=True)
if submitted and text.strip():
    storage.add_row("chat_messages", {
        "room_id": room_id,
        "user_id": user["id"],
        "message": text.strip(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })
    st.rerun()

if st.button("새로고침", use_container_width=True):
    st.rerun()
