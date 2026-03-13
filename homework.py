import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(page_title="우리 반 숙제 알리미", layout="wide", page_icon="🏫")

st.title("📅 우리 반 수행/숙제 알리미 PRO MAX")
st.write("반장이 매일매일 업데이트하는 우리 반 생존 캘린더! 🚀")

FILE_NAME = "homework_data.json"

# 데이터 불러오기
if 'tasks' not in st.session_state:
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

# 데이터 저장하기
def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=4)

# --- 사이드바: 반장 전용 관리자 모드 ---
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
                st.session_state.tasks.append({
                    "subject": new_sub,
                    "task": new_task,
                    "date": new_date.strftime("%Y-%m-%d")
                })
                save_data() 
                st.toast("새로운 과제가 달력에 추가되었습니다! 🎉")
                st.rerun()

# --- 메인 화면 ---
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
    st.balloons()
else:
    # 마감일 순서대로 정렬
    st.session_state.tasks.sort(key=lambda x: x['date'])

    # 💡 탭 3개로 나누기: 카드 / 캘린더 / 표
    tab1, tab2, tab3 = st.tabs(["📇 카드 뷰", "📅 진짜 달력 뷰 (NEW)", "📋 표 뷰 (한눈에)"])
    
    today = datetime.now().date()

    # [첫 번째 탭] 카드 뷰 (삭제는 여기서!)
    with tab1:
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
                        st.toast("과제가 성공적으로 삭제되었습니다! 👏")
                        st.rerun()
                st.markdown("---")

    # [두 번째 탭] 🚀 대망의 진짜 캘린더 뷰
    with tab2:
        st.markdown("### 🗓️ 이달의 우리 반 생존 캘린더")
        
        # 과목별로 달력에 표시될 색깔 지정하기 (센스 만점!)
        color_map = {
            "국어": "#FF6C6C", # 빨강
            "수학": "#4169E1", # 파랑
            "영어": "#FFBD45", # 노랑
            "과학": "#3CB371", # 초록
            "사회": "#9370DB", # 보라
            "역사": "#8B4513", # 갈색
            "기타": "#808080"  # 회색
        }
        
        calendar_events = []
        for task in st.session_state.tasks:
            # 과목에 맞는 색깔 꺼내오기
            color = color_map.get(task['subject'], "#FF4B4B")
            calendar_events.append({
                "title": f"[{task['subject']}] {task['task']}",
                "start": task['date'],
                "backgroundColor": color,
                "borderColor": color,
                "allDay": True
            })
            
        # 달력 세팅
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,dayGridWeek", # 월간/주간 보기 버튼
            },
            "initialView": "dayGridMonth", # 처음엔 월간(한 달) 보기로 시작
        }
        
        # 화면에 달력 그리기!
        calendar(events=calendar_events, options=calendar_options)

    # [세 번째 탭] 엑셀 같은 표 뷰
    with tab3:
        st.markdown("### 📋 전체 일정 리스트")
        df = pd.DataFrame(st.session_state.tasks)
        df.columns = ["과목", "과제 내용", "마감일"]
        
        def calculate_dday_for_table(date_str):
            t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            d = (t_date - today).days
            if d > 0: return f"D-{d}"
            elif d == 0: return "D-Day 🔥"
            else: return "마감됨"
        
        df["남은 기간"] = df["마감일"].apply(calculate_dday_for_table)
        st.dataframe(df, use_container_width=True, hide_index=True)
