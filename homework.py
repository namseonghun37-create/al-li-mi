import streamlit as st
import json
import os
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="우리 반 숙제 알리미", layout="wide", page_icon="🏫")

st.title("📅 10-3 알리미")

FILE_NAME = "homework_data.json"

# --- 1. 데이터 불러오기 ---
if 'tasks' not in st.session_state:
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=4)

# --- 2. 사이드바: 관리자 모드 ---
with st.sidebar:
    st.header("👑 반장 전용 관리자 모드")
    admin_pw = st.text_input("비밀번호를 입력하세요", type="password")

    is_admin = (admin_pw == "0206")

    if is_admin:
        st.success("관리자 로그인 성공")
        st.subheader("새로운 과제 추가")
        with st.form("add_task_form", clear_on_submit=True):
            # 💡 과목 선택과 직접 입력 칸을 같이 배치했습니다!
            new_sub = st.selectbox("과목 선택", ["국어", "수학", "영어", "과학", "사회", "역사", "기타"])
            custom_sub = st.text_input("✏️ 목록에 없는 과목 직접 입력 (선택사항)")
            
            new_task = st.text_input("과제 내용 (예: 프린트 2장)")
            new_date = st.date_input("마감일 선택")
            submitted = st.form_submit_button("과제 등록하기 📝")

            if submitted and new_task:
                # 💡 직접 입력 칸에 글자가 있으면 그걸 쓰고, 비어있으면 위에서 선택한 과목을 씁니다!
                final_sub = custom_sub.strip() if custom_sub.strip() else new_sub
                
                st.session_state.tasks.append({
                    "subject": final_sub,
                    "task": new_task,
                    "date": new_date.strftime("%Y-%m-%d")
                })
                save_data() 
                st.toast("과제가 추가되었습니다! 🎉")
                st.rerun()

# --- 3. 메인 화면 ---
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
else:
    # 마감일 순서대로 자동 정렬
    st.session_state.tasks.sort(key=lambda x: x['date'])
    today = datetime.now().date()

    # ==========================================
    # 🟢 파트 1: 디데이 카드 뷰
    # ==========================================
    st.subheader("🚨 다가오는 디데이 (급한 순서)")
    cols = st.columns(3)
    for i, task_info in enumerate(st.session_state.tasks):
        col = cols[i % 3]
        with col:
            st.markdown(f"### 📘 {task_info['subject']}")
            st.write(f"**내용:** {task_info['task']}")
            st.write(f"⏳ **마감일:** {task_info['date']}")

            target_date = datetime.strptime(task_info['date'], "%Y-%m-%d").date()
            d_day = (target_date - today).days

            if d_day > 0:
                st.info(f"**🚨 D-{d_day}**")
            elif d_day == 0:
                st.error("**🔥 D-Day (오늘 마감!)**")
            else:
                st.write(f"**✅ 기한 지남 (D+{-d_day})**")

            if is_admin:
                if st.button(f"완료/삭제 🗑️", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    save_data() 
                    st.rerun()
            st.markdown("---")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 🟢 파트 2: 진짜 달력 뷰
    # ==========================================
    st.subheader("🗓️캘린더")
    
    color_map = {
        "국어": "#FF6C6C", "수학": "#4169E1", "영어": "#FFBD45",
        "과학": "#3CB371", "사회": "#9370DB", "역사": "#8B4513", "기타": "#808080"
    }
    
    calendar_events = []
    for task in st.session_state.tasks:
        # 💡 직접 입력한 과목은 기본 색상(청록색 느낌)으로 표시되게 설정!
        color = color_map.get(task['subject'], "#17a2b8")
        
        calendar_events.append({
            "title": f"[{task['subject']}] {task['task']}",
            "start": task['date'],
            "color": color, 
            "allDay": True
        })
        
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth",
        },
        "initialView": "dayGridMonth",
        "height": 600,
    }
    
    calendar(events=calendar_events, options=calendar_options)
