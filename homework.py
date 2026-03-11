import streamlit as st
import datetime
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 수행/숙제 알리미", page_icon="📅", layout="wide")

# 스타일 설정 (깔끔한 카드 느낌)
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .d-day-red { color: #FF4B4B; font-size: 24px; font-weight: bold; }
    .d-day-orange { color: #FFA500; font-size: 24px; font-weight: bold; }
    .d-day-green { color: #00CC96; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 초기 데이터 세팅 (발표 때 보여주기 위한 가짜 데이터)
if 'tasks' not in st.session_state:
    today = datetime.date.today()
    st.session_state.tasks = [
        {"subject": "국어", "task": "1단원 독후감 제출", "due_date": today + datetime.timedelta(days=2)},
        {"subject": "수학", "task": "교과서 54p~60p 풀기", "due_date": today + datetime.timedelta(days=5)},
        {"subject": "영어", "task": "수행평가 단어 시험", "due_date": today + datetime.timedelta(days=10)},
    ]

# 3. D-Day 계산 함수
def calculate_dday(due_date):
    today = datetime.date.today()
    delta = (due_date - today).days
    if delta == 0:
        return "D-Day", "red"
    elif delta < 0:
        return f"마감됨", "grey"
    elif delta <= 3:
        return f"D-{delta}", "red"
    elif delta <= 7:
        return f"D-{delta}", "orange"
    else:
        return f"D-{delta}", "green"

# ==========================================
# 메인 화면: 학생들(친구들)이 보는 화면
# ==========================================
st.title("📅 우리 반 수행/숙제 캘린더")
st.markdown("반장이 매일매일 업데이트하는 우리 반 생존 알리미! 🚀")
st.divider()

# 과제 목록을 날짜순으로 정렬
sorted_tasks = sorted(st.session_state.tasks, key=lambda x: x['due_date'])

if not sorted_tasks:
    st.success("🎉 현재 등록된 과제가 없습니다! 푹 쉬세요!")
else:
    # 3열로 나누어서 카드처럼 예쁘게 배치
    cols = st.columns(3)
    for idx, task in enumerate(sorted_tasks):
        dday_text, color_class = calculate_dday(task['due_date'])
        
        # 이미 마감된 숙제는 건너뛰기
        if color_class == "grey": continue 
        
        with cols[idx % 3]: # 3칸씩 번갈아가며 채우기
            with st.container(border=True):
                st.markdown(f"<span class='d-day-{color_class}'>{dday_text}</span>", unsafe_allow_html=True)
                st.markdown(f"<p class='big-font'>📘 {task['subject']}</p>", unsafe_allow_html=True)
                st.write(f"**내용:** {task['task']}")
                st.caption(f"📅 마감일: {task['due_date'].strftime('%Y년 %m월 %d일')}")

# ==========================================
# 사이드바: 반장 전용 관리자 모드
# ==========================================
with st.sidebar:
    st.header("👑 반장 전용 관리자 모드")
    admin_pw = st.text_input("비밀번호를 입력하세요)", type="password")
    
    if admin_pw == "0206":
        st.success("관리자 로그인 성공!")
        st.subheader("새로운 과제 추가")
        
        with st.form("add_task_form", clear_on_submit=True):
            new_sub = st.selectbox("과목", ["국어", "수학", "영어", "사회", "과학", "기타"])
            new_task = st.text_input("과제 내용 (예: 프린트 2장 풀기)")
            new_date = st.date_input("마감일 선택", min_value=datetime.date.today())
            
            submitted = st.form_submit_button("과제 등록하기 🚀")
            if submitted:
                if new_task:
                    st.session_state.tasks.append({
                        "subject": new_sub, 
                        "task": new_task, 
                        "due_date": new_date
                    })
                    st.toast("✅ 새로운 숙제가 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("과제 내용을 입력해주세요!")
