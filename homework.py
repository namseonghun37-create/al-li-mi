import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="10-3 알리미", layout="wide")

st.title("10-3 알리미")
st.write("반장이 매일매일 업데이트하는 우리 알리미")

# 파일에 저장하는 세팅
FILE_NAME = "homework_data.json"

if 'tasks' not in st.session_state:
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=4)

# 사이드바: 반장 전용 관리자 모드
with st.sidebar:
    st.header("👑 반장 전용 관리자 모드")
    admin_pw = st.text_input("비밀번호를 입력하세요", type="password")

    is_admin = (admin_pw == "0206")

    if is_admin:
        st.success("관리자 로그인 성공! 😎")
        st.subheader("새로운 과제 추가")
        with st.form("add_task_form", clear_on_submit=True):
            new_sub = st.selectbox("과목", ["국어", "수학", "영어", "과학", "사회", "역사", "기타"])
            new_task = st.text_input("과제 내용 (예: 프린트 2장)")
            new_date = st.date_input("마감일 선택")
            submitted = st.form_submit_button("과제 등록하기 📝")

            if submitted and new_task:
                st.session_state.tasks.append({
                    "subject": new_sub,
                    "task": new_task,
                    "date": new_date.strftime("%Y-%m-%d")
                })
                save_data() 
                st.rerun()

# 메인 화면: 숙제 목록 보여주기
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
else:
    cols = st.columns(3)
    
    # 💡 오늘 날짜 가져오기 (디데이 계산용)
    today = datetime.now().date()
    
    for i, task_info in enumerate(st.session_state.tasks):
        col = cols[i % 3]
        with col:
            st.markdown(f"### 📘 {task_info['subject']}")
            st.write(f"**내용:** {task_info['task']}")
            st.write(f"⏳ **마감일:** {task_info['date']}")

            # --- 🚀 대망의 디데이 계산 로직 ---
            target_date = datetime.strptime(task_info['date'], "%Y-%m-%d").date()
            d_day = (target_date - today).days

            if d_day > 0:
                # 기한이 남았을 때 (파란색 알림)
                st.info(f"**🚨 D-{d_day}**")
            elif d_day == 0:
                # 오늘이 마감일 때 (빨간색 경고!)
                st.error("**🔥 D-Day (오늘 마감!)**")
            else:
                # 기한이 지났을 때 (회색 느낌)
                st.write(f"**✅ 기한 지남 (D+{-d_day})**")
            # --------------------------------

            if is_admin:
                if st.button(f"완료/삭제 🗑️", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    save_data() 
                    st.rerun()
            st.markdown("---")
