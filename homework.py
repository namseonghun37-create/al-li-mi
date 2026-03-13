import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="우리 반 숙제 알리미", layout="wide", page_icon="🏫")

st.title("📅 우리 반 수행/숙제 알리미 PRO")
st.write("반장이 매일매일 업데이트하는 우리 반 생존 알리미! 🚀")

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
                st.toast("새로운 과제가 추가되었습니다! 🎉") # 스마트폰 푸시 알림 같은 효과
                st.rerun()

# --- 메인 화면: 숙제 목록 보여주기 ---
if not st.session_state.tasks:
    st.info("현재 등록된 과제/수행평가가 없습니다! 🎉 다들 푹 쉬세요!")
    st.balloons() # 숙제가 없으면 풍선 날리기!
else:
    # 💡 마감일이 빠른 순서대로(급한 순서대로) 자동 정렬!
    st.session_state.tasks.sort(key=lambda x: x['date'])

    # 💡 탭(Tab) 만들기: 카드 뷰 vs 달력(표) 뷰
    tab1, tab2 = st.tabs(["📇 카드 뷰 (기본)", "📅 달력/일정표 뷰 (한눈에)"])
    
    today = datetime.now().date()

    # [첫 번째 탭] 기존의 예쁜 카드 모양
    with tab1:
        cols = st.columns(3)
        for i, task_info in enumerate(st.session_state.tasks):
            col = cols[i % 3]
            with col:
                st.markdown(f"### 📘 {task_info['subject']}")
                st.write(f"**내용:** {task_info['task']}")
                st.write(f"⏳ **마감일:** {task_info['date']}")

                # 디데이 계산 로직
                target_date = datetime.strptime(task_info['date'], "%Y-%m-%d").date()
                d_day = (target_date - today).days

                if d_day > 0:
                    st.info(f"**🚨 D-{d_day}**")
                elif d_day == 0:
                    st.error("**🔥 D-Day (오늘 마감!)**")
                else:
                    st.write(f"**✅ 기한 지남 (D+{-d_day})**")

                # 관리자 삭제 버튼
                if is_admin:
                    if st.button(f"완료/삭제 🗑️", key=f"del_{i}"):
                        st.session_state.tasks.pop(i)
                        save_data() 
                        st.toast("과제가 성공적으로 삭제되었습니다! 👏")
                        st.rerun()
                st.markdown("---")

    # [두 번째 탭] 캘린더/일정표 모양 (전체 한눈에 보기)
    with tab2:
        st.markdown("### 🗓️ 우리 반 전체 일정 한눈에 보기")
        
        # 데이터를 표(Dataframe) 형식으로 변환해서 보여주기
        df = pd.DataFrame(st.session_state.tasks)
        df.columns = ["과목", "과제 내용", "마감일"] # 영어 이름을 한글로 예쁘게 변경
        
        # 표 안에도 D-Day 계산해서 넣어주기
        def calculate_dday_for_table(date_str):
            t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            d = (t_date - today).days
            if d > 0: return f"D-{d}"
            elif d == 0: return "D-Day 🔥"
            else: return "마감됨"
        
        df["남은 기간"] = df["마감일"].apply(calculate_dday_for_table)
        
        # 화면에 꽉 차게 예쁜 표 그려주기
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if is_admin:
            st.warning("💡 삭제는 '카드 뷰' 탭으로 돌아가서 버튼을 눌러주세요!")
