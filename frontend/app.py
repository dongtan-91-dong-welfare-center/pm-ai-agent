"""
Streamlit 앱 진입점 - 원자재 관리 AI 에이전트
"Digital Colleague" - 온프레미스 기반
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import streamlit as st

st.set_page_config(
    page_title="MatAgent | Digital Colleague",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark glass sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid rgba(48, 215, 150, 0.2);
    }
    
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: #0d1117;
    }
    
    /* Metric cards - glassmorphism */
    [data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid rgba(48, 215, 150, 0.15);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* KPI metric value */
    [data-testid="stMetricValue"] {
        color: #30d796 !important;
        font-weight: 700;
    }
    
    /* Headings */
    h1, h2, h3 { color: #f0f6fc !important; }
    p, span, label { color: #8b949e !important; }
    
    /* Alert box */
    .alert-box {
        background: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.4);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        color: #f85149 !important;
    }
    
    /* Section divider */
    hr { border-color: rgba(48, 215, 150, 0.15) !important; }
    
    /* Sidebar nav text */
    [data-testid="stSidebar"] * { color: #8b949e !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #30d796 !important; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🏭 MatAgent")
    st.markdown("**On-premise AI Agent**")
    st.markdown("원자재 관리 디지털 동료")
    st.divider()
    st.markdown("### 📋 Navigation")
    st.page_link("app.py", label="🏠 홈", icon=None)
    st.page_link("pages/01_dashboard.py", label="📊 재고 대시보드")
    st.page_link("pages/02_agent.py", label="🤖 Digital Colleague")
    st.divider()
    st.caption("v1.0.0 | On-premise MVP")

# --- Home Page ---
st.title("🏭 MatAgent — 원자재 관리 AI 에이전트")
st.markdown("""
<p style='font-size:1.1rem; color:#8b949e;'>
내부망(On-premise) 기반 AI 에이전트로, 원자재 관리 담당자의 <strong style='color:#30d796;'>데이터 기반 의사결정</strong>을 지원합니다.
</p>
""", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    ### 📊 재고 대시보드
    실시간 재고 현황, 안전 재고 임계치, 공급사 리드타임을 한눈에 확인하세요.
    """)
    st.page_link("pages/01_dashboard.py", label="대시보드 열기 →")

with col2:
    st.markdown("""
    ### 🤖 Digital Colleague
    AI 디지털 동료와 자연어로 대화하며 위험 재고 분석, 공급사 현황을 파악하세요.
    """)
    st.page_link("pages/02_agent.py", label="채팅 시작 →")

with col3:
    st.markdown("""
    ### 🔔 자동 알림
    `current_stock < safety_stock` 조건 감지 시 선제적 경고를 자동으로 발송합니다.
    """)
    st.info("Rule-based 알림 시스템 활성화 중", icon="✅")
