import streamlit as st
import json
import os

st.set_page_config(page_title="우리 반 숙제 알리미", layout="wide")

st.title("📅 우리 반 수행/숙제 캘린더")
st.write("반장이 매일매일 업데이트하는 우리 반 생존 알리미! 🚀")

# --- 💡 핵심: 파일에 영구 저장하는 마법의 세팅 ---
FILE_NAME = "homework_data.json"

# 1. 파일에서 기존 숙제 불러오기
if 'tasks' not in st.session_state:
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

# 2. 파일을 업데이트(저장)하는 함수
def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=4)
# ------------------------------------------------

# 사이드바: 반장 전용 관리자 모드
with st.sidebar:
    st.header("👑 반장 전용 관리자 모드")
    admin_pw = st.text_input("비밀번호를 입력하세요", type="password")

    is_admin = (admin_pw == "1234")

    if is_admin:
        st.success("관리자 로그인 성공! 😎")
        st.subheader("새로운 과제 추가")
        with st.form("add_task_form", clear_on_submit=True):
            new_sub = st.selectbox("과목", ["국어", "수학", "영어", "과학", "사회", "역사", "기타"])
            new_task = st.text_input("과제 내용 (예: 프린트 2장)")
            new_date = st.date_input("마감일 선택")
            submitted = st.form_submit_button("과제 등록하기 📝")

            if submitted and new_task:
                # 숙제 추가하고
                st.session_state.tasks.append({
                    "subject": new_sub,
                    "task": new_task,
                    "date": new_date.strftime("%Y-%m-%d")
                })
                # 파일에 도장 쾅! (저장)
                save_data() 
                st.rerun()

# 메인 화면: 숙제 목록 보여주기
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
else:
    cols = st.columns(3)
    for i, task_info in enumerate(st.session_state.tasks):
        col = cols[i % 3]
        with col:
            st.markdown(f"### 📘 {task_info['subject']}")
            st.write(f"**내용:** {task_info['task']}")
            st.write(f"⏳ **마감일:** {task_info['date']}")

            if is_admin:
                if st.button(f"완료/삭제 🗑️", key=f"del_{i}"):
                    # 숙제 지우고
                    st.session_state.tasks.pop(i)
                    # 지운 상태를 파일에 도장 쾅! (저장)
                    save_data() 
                    st.rerun()
            st.markdown("---")
