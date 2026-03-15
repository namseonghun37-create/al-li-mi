import streamlit as st
import json
import requests
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="우리 반 숙제 알리미", layout="wide", page_icon="🏫")

st.title("📅 우리 반 수행/숙제 생존 알리미 PRO MAX")
st.write("디데이도 짠! 달력도 짠! 한 화면에서 모두 확인하세요 🚀")

# ==========================================
# 🔑 여기에 아까 복사한 2개를 붙여넣으세요! 
BIN_ID = "69b64af5b7ec241ddc6d090c"  # 예: "65b12..." 
API_KEY = "$2a$10$3cG/OajFjHqETdapVtD6c.DiWYydIXK/S4IESXoyT.O4vXTJDDSHy"  # 예: "$2a$10$..."
# ==========================================

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- 1. 인터넷 금고에서 데이터 불러오기 ---
def load_data():
    try:
        response = requests.get(URL, headers={"X-Master-Key": API_KEY})
        if response.status_code == 200:
            data = response.json()
            return data.get("record", {}).get("tasks", [])
    except Exception as e:
        st.error("데이터를 불러오지 못했습니다.")
    return []

# --- 2. 인터넷 금고에 데이터 저장하기 ---
def save_data():
    try:
        req_data = {"tasks": st.session_state.tasks}
        requests.put(URL, json=req_data, headers=HEADERS)
    except Exception as e:
        st.error("데이터 저장에 실패했습니다.")

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()

# --- 3. 사이드바: 관리자 모드 ---
with st.sidebar:
    st.header("👑 반장 전용 관리자 모드")
    admin_pw = st.text_input("비밀번호를 입력하세요", type="password")

    is_admin = (admin_pw == "1234")

    if is_admin:
        st.success("관리자 로그인 성공! 😎")
        st.subheader("새로운 과제 추가")
        with st.form("add_task_form", clear_on_submit=True):
            new_sub = st.selectbox("과목 선택", ["국어", "수학", "영어", "과학", "사회", "역사", "기타"])
            custom_sub = st.text_input("✏️ 목록에 없는 과목 직접 입력 (선택사항)")
            
            new_task = st.text_input("과제 내용 (예: 프린트 2장)")
            new_date = st.date_input("마감일 선택")
            submitted = st.form_submit_button("과제 등록하기 📝")

            if submitted and new_task:
                final_sub = custom_sub.strip() if custom_sub.strip() else new_sub
                
                st.session_state.tasks.append({
                    "subject": final_sub,
                    "task": new_task,
                    "date": new_date.strftime("%Y-%m-%d")
                })
                save_data() 
                st.toast("과제가 안전한 금고에 추가되었습니다! 🎉")
                st.rerun()

# --- 4. 메인 화면 ---
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
else:
    st.session_state.tasks.sort(key=lambda x: x['date'])
    today = datetime.now().date()

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

    st.subheader("🗓️ 한눈에 보는 이달의 캘린더")
    color_map = {
        "국어": "#FF6C6C", "수학": "#4169E1", "영어": "#FFBD45",
        "과학": "#3CB371", "사회": "#9370DB", "역사": "#8B4513", "기타": "#808080"
    }
    
    calendar_events = []
    for task in st.session_state.tasks:
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
