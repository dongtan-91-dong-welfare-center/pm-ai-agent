"""
Dashboard Page - 재고 현황 대시보드
real-time KPI cards + Plotly charts
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="대시보드 | MatAgent", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid rgba(48, 215, 150, 0.2); }
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stMetric"] { background: rgba(22, 27, 34, 0.8); border: 1px solid rgba(48, 215, 150, 0.15); border-radius: 12px; padding: 1rem; }
[data-testid="stMetricValue"] { color: #30d796 !important; font-weight: 700; }
h1, h2, h3 { color: #f0f6fc !important; }
p, span, label { color: #8b949e !important; }
hr { border-color: rgba(48, 215, 150, 0.15) !important; }
[data-testid="stSidebar"] * { color: #8b949e !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #30d796 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏭 MatAgent")
    st.divider()
    st.page_link("app.py", label="🏠 홈")
    st.page_link("pages/01_dashboard.py", label="📊 재고 대시보드")
    st.page_link("pages/02_agent.py", label="🤖 Digital Colleague")

# --- Sample Data ---
materials = pd.DataFrame({
    "item_name": ["알루미늄 플레이트", "스틸 로드", "구리 와이어", "탄소 섬유", "티타늄 합금"],
    "category": ["금속", "금속", "금속", "복합재", "금속"],
    "current_stock": [450, 1200, 300, 85, 220],
    "safety_stock": [500, 1000, 400, 100, 200],
    "threshold": [400, 800, 350, 80, 180],
    "unit": ["kg", "pcs", "m", "kg", "kg"],
})

suppliers = pd.DataFrame({
    "supplier": ["Global Metals Ltd.", "Fast Sourcing Inc.", "Eco Materials Co.", "KD Steel", "AluCo Asia"],
    "lead_time": [14, 7, 21, 10, 12],
    "risk_score": [0.2, 0.5, 0.1, 0.35, 0.25],
    "on_time_rate": [98, 92, 96, 88, 94],
})

# --- Alerts ---
alerts = materials[materials["current_stock"] < materials["safety_stock"]]

# --- Header ---
st.title("📊 재고 현황 대시보드")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.caption(f"마지막 업데이트: {current_time}")

# Alerts
if not alerts.empty:
    st.markdown("---")
    for _, row in alerts.iterrows():
        st.error(
            f"⚠️ **{row['item_name']}** — 안전 재고 미달 "
            f"(현재: {row['current_stock']} {row['unit']} / 안전기준: {row['safety_stock']} {row['unit']})",
            icon=None
        )

st.divider()

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
total_items = len(materials)
alert_count = len(alerts)
avg_lead = int(suppliers["lead_time"].mean())
high_risk = len(suppliers[suppliers["risk_score"] > 0.4])

col1.metric("📦 전체 품목수", total_items, "활성")
col2.metric("🚨 위험 품목수", alert_count, f"-{alert_count}" if alert_count else "정상", delta_color="inverse")
col3.metric("🚚 평균 리드타임", f"{avg_lead}일", "최근 7일 기준")
col4.metric("⚡ 고위험 공급사", high_risk, f"{high_risk}개 모니터링", delta_color="inverse")

st.divider()

# --- Charts Row 1 ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("재고 현황 vs 안전 재고")
    fig_stock = go.Figure()
    fig_stock.add_trace(go.Bar(
        x=materials["item_name"], y=materials["current_stock"],
        name="현재 재고",
        marker_color=["#f85149" if r["current_stock"] < r["safety_stock"] else "#30d796"
                      for _, r in materials.iterrows()],
        opacity=0.9,
    ))
    fig_stock.add_trace(go.Scatter(
        x=materials["item_name"], y=materials["safety_stock"],
        name="안전 재고선", mode="lines+markers",
        line=dict(color="#f0a030", dash="dash", width=2),
        marker=dict(size=8),
    ))
    fig_stock.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e", legend_font_color="#8b949e",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont_color="#8b949e"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont_color="#8b949e"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig_stock, use_container_width=True)

with chart_col2:
    st.subheader("공급사 리드타임 비교")
    fig_lead = px.bar(
        suppliers, x="supplier", y="lead_time",
        color="risk_score", color_continuous_scale=["#30d796", "#f0a030", "#f85149"],
        labels={"lead_time": "리드타임(일)", "supplier": "공급사", "risk_score": "위험도"},
    )
    fig_lead.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e",
        coloraxis_colorbar=dict(tickfont=dict(color="#8b949e"), title=dict(font=dict(color="#8b949e"))),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e")),
        margin=dict(l=0, r=0, t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig_lead, use_container_width=True)

# --- Charts Row 2 ---
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("재고 추이 (최근 30일)")
    dates = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    trend_data = pd.DataFrame({
        "날짜": dates,
        "알루미늄": [450 + random.randint(-50, 30) for _ in range(30)],
        "스틸 로드": [1200 + random.randint(-100, 50) for _ in range(30)],
        "구리 와이어": [300 + random.randint(-40, 20) for _ in range(30)],
    })
    fig_trend = px.line(
        trend_data.melt(id_vars="날짜", var_name="품목", value_name="재고"),
        x="날짜", y="재고", color="품목",
        color_discrete_sequence=["#30d796", "#58a6ff", "#f0a030"],
    )
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e", legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e")),
        margin=dict(l=0, r=0, t=20, b=0),
        height=280,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col4:
    st.subheader("공급사 납기 준수율")
    fig_ontime = px.bar(
        suppliers, x="on_time_rate", y="supplier", orientation="h",
        color="on_time_rate", color_continuous_scale=["#f85149", "#f0a030", "#30d796"],
        range_color=[80, 100],
        labels={"on_time_rate": "납기 준수율(%)", "supplier": ""}
    )
    fig_ontime.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e",
        coloraxis_colorbar=dict(tickfont=dict(color="#8b949e"), title=dict(font=dict(color="#8b949e"))),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e"), range=[80, 100]),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8b949e")),
        margin=dict(l=0, r=0, t=20, b=0),
        height=280,
    )
    st.plotly_chart(fig_ontime, use_container_width=True)

# --- Data Table ---
st.divider()
st.subheader("📋 원자재 상세 현황")

def highlight_stock(row):
    if row["current_stock"] < row["safety_stock"]:
        return ["background-color: rgba(248,81,73,0.1); color: #f85149"] * len(row)
    return [""] * len(row)

styled = materials.style.apply(highlight_stock, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)
