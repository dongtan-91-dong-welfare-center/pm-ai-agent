"""
Digital Colleague Page - AI 에이전트 채팅 인터페이스
Rule-based alerts + Scenario-based mock AI responses
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Digital Colleague | MatAgent", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid rgba(48, 215, 150, 0.2); }
[data-testid="stAppViewContainer"] { background: #0d1117; }
h1, h2, h3 { color: #f0f6fc !important; }
p, label { color: #8b949e !important; }
hr { border-color: rgba(48, 215, 150, 0.15) !important; }
[data-testid="stSidebar"] * { color: #8b949e !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #30d796 !important; }

/* Chat input styling */
[data-testid="stChatInput"] {
    background: rgba(22, 27, 34, 0.9) !important;
    border: 1px solid rgba(48, 215, 150, 0.3) !important;
    border-radius: 12px !important;
}

/* Quick action buttons */
.stButton button {
    background: rgba(48, 215, 150, 0.1);
    border: 1px solid rgba(48, 215, 150, 0.3);
    color: #30d796 !important;
    border-radius: 8px;
    font-size: 0.85rem;
    transition: all 0.2s;
}
.stButton button:hover {
    background: rgba(48, 215, 150, 0.2);
    border-color: #30d796;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏭 MatAgent")
    st.divider()
    st.page_link("app.py", label="🏠 홈")
    st.page_link("pages/01_dashboard.py", label="📊 재고 대시보드")
    st.page_link("pages/02_agent.py", label="🤖 Digital Colleague")
    st.divider()
    st.markdown("### 🔔 실시간 알림")
    st.error("⚠️ 알루미늄 플레이트 안전재고 미달", icon=None)
    st.error("⚠️ 구리 와이어 안전재고 미달", icon=None)
    st.warning("🚚 공급사 C 납기 지연 3일", icon=None)
    st.divider()
    if st.button("💬 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

import requests
import json
import re

# --- API Configuration ---
API_BASE_URL = "http://localhost:8000/v1"

# --- Helper: Report Generation ---
def fetch_report(report_type: str):
    try:
        res = requests.get(f"{API_BASE_URL}/report/excel", params={"type": report_type})
        if res.status_code == 200:
            return res.content
        return None
    except:
        return None

# --- AI Response Engine ---
def get_agent_response(query: str):
    """
    백엔드 API를 호출하여 에이전트 응답을 가져옵니다.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/chat", params={"query": query})
        if response.status_code == 200:
            return response.json().get("response", "응답을 파싱할 수 없습니다.")
        else:
            return f"에러 발생: {response.status_code}"
    except Exception as e:
        return f"연결 실패: {str(e)}"

# --- Chat Page ---
st.title("🤖 Digital Colleague")
st.markdown("<p style='color:#8b949e;'>ReAct 기반 지능형 에이전트와 원자재 관리에 대해 자연어로 대화하세요.</p>", unsafe_allow_html=True)
st.divider()

# --- Reports & Tools ---
with st.expander("🛠️ 데이터 도구 및 리포트", expanded=False):
    st.markdown("특수 분석 리포트를 엑셀로 다운로드할 수 있습니다.")
    rep_col1, rep_col2, rep_col3 = st.columns(3)
    
    # Inventory Report
    if rep_col1.button("📦 전체 재고 리포트", use_container_width=True):
        data = fetch_report("inventory")
        if data:
            st.download_button("Excel 다운로드", data, "inventory_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="btn_inv")

    # NC Report
    if rep_col2.button("🔴 부적합/보류 리포트", use_container_width=True):
        data = fetch_report("nc")
        if data:
            st.download_button("Excel 다운로드", data, "nc_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="btn_nc")
            
    # Material Master
    if rep_col3.button("🏭 자재 마스터 리포트", use_container_width=True):
        data = fetch_report("material")
        if data:
            st.download_button("Excel 다운로드", data, "material_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="btn_mat")

st.divider()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Proactive greeting from agent
    proactive_msg = (
        "안녕하세요! 저는 당신의 **Digital Colleague** 입니다. 👋\n\n"
        "현재 시스템 기준일은 **2026-03-26** 입니다. "
        "재고 현황, BOM 구조, 공급망 리스크 등 원자재 관리 업무를 도와드릴 수 있습니다.\n\n"
        "무엇을 분석해 드릴까요?"
    )
    st.session_state.messages.append({"role": "assistant", "content": proactive_msg})

if "triggered_reports" not in st.session_state:
    st.session_state.triggered_reports = set()

# Quick Actions
st.markdown("**빠른 질문:**")
qa_cols = st.columns(4)
quick_questions = [
    "현재 재고 상태 알려줘",
    "규석 주사제 생산 문제 없어?",
    "납기 지연 발주 건 확인해줘",
    "부적합 자재 리스크 요약해줘",
]
for i, q in enumerate(quick_questions):
    if qa_cols[i].button(q, use_container_width=True, key=f"qa_{i}"):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.spinner("에이전트 추론 중..."):
            response = get_agent_response(q)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

st.divider()

# Display Messages
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        content = msg["content"]
        
        # Parse Tags
        download_match = re.search(r"\[DOWNLOAD_EXCEL:(.*?)\]", content)
        suggest_match = re.search(r"\[SUGGEST_EXCEL:(.*?)\]", content)
        
        # Clean text
        display_text = re.sub(r"\[(DOWNLOAD|SUGGEST)_EXCEL:.*?\]", "", content).strip()
        st.markdown(display_text)
        
        # Handle Assistant-only buttons
        if msg["role"] == "assistant":
            # 1. Direct Download Button
            if download_match:
                rep_type = download_match.group(1).strip()
                excel_data = fetch_report(rep_type)
                if excel_data:
                    st.download_button(
                        label=f"📥 {rep_type.upper()} 리포트 다운로드",
                        data=excel_data,
                        file_name=f"{rep_type}_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{idx}"
                    )
            
            # 2. Interactive Suggestion Button
            elif suggest_match:
                rep_type = suggest_match.group(1).strip()
                if f"trig_{idx}" in st.session_state.triggered_reports:
                    excel_data = fetch_report(rep_type)
                    if excel_data:
                        st.download_button(
                            label=f"📥 {rep_type.upper()} 리포트 다운로드",
                            data=excel_data,
                            file_name=f"{rep_type}_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_suggested_{idx}"
                        )
                else:
                    if st.button(f"📊 상세 내역을 엑셀로 확인하시겠습니까? ({rep_type})", key=f"sug_{idx}"):
                        st.session_state.triggered_reports.add(f"trig_{idx}")
                        st.rerun()

# Chat Input
if prompt := st.chat_input("원자재 관련 질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("분석 중..."):
            response = get_agent_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
