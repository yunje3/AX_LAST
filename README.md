# TeamSync Manager

Streamlit 기반 팀 프로젝트/일정/채팅 관리 테스트 버전입니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 테스트 계정

| 권한 | 이메일 | 비밀번호 |
| --- | --- | --- |
| Admin | admin@teamsync.test | admin123 |
| Manager | manager@teamsync.test | manager123 |
| Member | member@teamsync.test | member123 |

## Streamlit Cloud 배포

GitHub 업로드 시 숨김 폴더가 불편할 수 있어 `.streamlit/` 폴더는 사용하지 않습니다. Streamlit Cloud에서 Repository를 연결하고 Main file path를 `app.py`로 지정하면 됩니다.

## 저장 방식

현재 버전은 DB 없이 `data/*.json` 샘플 데이터를 읽고, 실행 중 변경사항은 `st.session_state`에 저장합니다. Streamlit Cloud에서는 세션이 초기화되면 변경사항이 사라질 수 있습니다.

