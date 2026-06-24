from __future__ import annotations

import streamlit as st

from src import storage


def login(email: str, password: str) -> bool:
    storage.init_state()
    for user in st.session_state.users:
        if (
            user.get("email", "").lower() == email.lower().strip()
            and user.get("password") == password
            and user.get("is_active", True)
        ):
            st.session_state.current_user = {key: value for key, value in user.items() if key != "password"}
            st.session_state.authenticated = True
            return True
    return False


def logout() -> None:
    st.session_state.pop("current_user", None)
    st.session_state.authenticated = False


def current_user() -> dict | None:
    return st.session_state.get("current_user")


def require_login() -> dict | None:
    user = current_user()
    if not user:
        st.warning("로그인이 필요합니다. 왼쪽 메뉴의 메인 화면에서 로그인해 주세요.")
        st.stop()
    return user


def is_admin() -> bool:
    user = current_user()
    return bool(user and user.get("role") == "Admin")


def is_manager_or_admin() -> bool:
    user = current_user()
    return bool(user and user.get("role") in {"Admin", "Manager"})
