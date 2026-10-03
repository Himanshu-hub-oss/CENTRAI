import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import get_db_connection, seed_database_with_data
from dashboard.components import apply_custom_css, render_metric_card

st.set_page_config(
    page_title="SkillCentre Guardian AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()
seed_database_with_data()

# Header & Government Tagline
st.markdown('<div class="header-title">🛡️ SkillCentre Guardian AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Government of India | Ministry of Skill Development & Entrepreneurship — AI Decision-Support Platform</div>', unsafe_allow_html=True)

st.markdown('<span class="flag-label">Prototype / Synthetic Operational Data</span>', unsafe_allow_html=True)
st.write("")

# System Status Bar Required by SIH Specification
st.markdown("""
<div style="background: #0f172a; padding: 10px 18px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #1e293b;">
    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">SYSTEM HEALTH METRICS:</div>
    <div style="font-size: 0.85rem; font-weight: 600;">
        <span style="color: #4ade80; margin-right: 15px;">● Camera: ONLINE (35/35)</span>
        <span style="color: #4ade80; margin-right: 15px;">● AI Detection: ACTIVE</span>
        <span style="color: #4ade80; margin-right: 15px;">● Attendance Data: SYNCED</span>
        <span style="color: #4ade80; margin-right: 15px;">● Infrastructure: MONITORED</span>
        <span style="color: #facc15; margin-right: 15px;">● Alerts: 7 PENDING</span>
        <span style="color: #4ade80;">● Database: CONNECTED</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Database Query
conn = get_db_connection()
df_centres = pd.read_sql_query("SELECT * FROM training_centres", conn)
df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)
conn.close()

# Sidebar Filters
st.sidebar.image("https://img.icons8.com/color/96/000000/shield.png", width=64)
st.sidebar.title("Guardian Navigation")
st.sidebar.markdown("---")

selected_state = st.sidebar.selectbox("Filter by State", ["All States"] + list(df_centres['state'].unique()))
if selected_state != "All States":
    filtered_df = df_centres[df_centres['state'] == selected_state]
else:
    filtered_df = df_centres

selected_district = st.sidebar.selectbox("Filter by District", ["All Districts"] + list(filtered_df['district'].unique()))
if selected_district != "All Districts":
    filtered_df = filtered_df[filtered_df['district'] == selected_district]

st.sidebar.markdown("---")
st.sidebar.info("💡 **SIH 2026 Problem SIH26245**: Real-time AI monitoring for skill training centres, privacy-preserving attendance, behaviour indicator & transparent risk engine.")

# Top Metrics Row
c1, c2, c3, c4, c5 = st.columns(5)

total_centres = len(filtered_df)
high_risk_cnt = len(filtered_df[filtered_df['risk_level'] == 'HIGH RISK'])
avg_att = filtered_df['attendance_pct'].mean()
avg_comp = filtered_df['infra_compliance_pct'].mean()
open_alerts_cnt = len(df_alerts[df_alerts['status'] == 'Open'])

with c1:
    render_metric_card("Total Centres", f"{total_centres}", "Active Monitored Hubs")
with c2:
    render_metric_card("High Risk Centres", f"{high_risk_cnt}", "Requires Immediate Audit", color="#dc2626")
with c3:
    render_metric_card("Avg Occupancy", f"{avg_att:.1f}%", "AI Estimated Attendance")
with c4:
    render_metric_card("Compliance Rate", f"{avg_comp:.1f}%", "AI & Officer Verified")
with c5:
    render_metric_card("Open AI Alerts", f"{open_alerts_cnt}", "Pending Verification", color="#d97706")

st.markdown("---")

# Layout: Visual Charts
col_left, col_right = st.columns([1.2, 1.0])

with col_left:
    st.subheader("📍 State & District Risk Distribution")
    fig_bar = px.bar(
        filtered_df,
        x="district",
        y="risk_score",
        color="risk_level",
        hover_data=["centre_name", "course", "attendance_pct"],
        color_discrete_map={"LOW RISK": "#16a34a", "MEDIUM RISK": "#d97706", "HIGH RISK": "#dc2626"},
        title="Training Centre Risk Score by District",
        labels={"risk_score": "Risk Score (0-100)", "district": "District"}
    )
    fig_bar.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📊 Operational Risk Categorization")
    risk_counts = filtered_df['risk_level'].value_counts().reset_index()
    risk_counts.columns = ['risk_level', 'count']
    fig_pie = px.pie(
        risk_counts,
        names="risk_level",
        values="count",
        color="risk_level",
        color_discrete_map={"LOW RISK": "#16a34a", "MEDIUM RISK": "#d97706", "HIGH RISK": "#dc2626"},
        hole=0.45,
        title="Centre Risk Level Ratios"
    )
    fig_pie.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# High-Risk Centres Priority Watchlist Table
st.subheader("⚠️ Priority Action Required: High & Medium Risk Centres")
risk_table_df = filtered_df[filtered_df['risk_level'].isin(['HIGH RISK', 'MEDIUM RISK'])][
    ['centre_id', 'centre_name', 'state', 'district', 'attendance_pct', 'infra_compliance_pct', 'engagement_score', 'risk_score', 'risk_level', 'open_alerts']
].sort_values(by="risk_score", ascending=False)

st.dataframe(
    risk_table_df,
    column_config={
        "centre_id": "Centre ID",
        "centre_name": "Hub Name",
        "attendance_pct": st.column_config.NumberColumn("Occupancy %", format="%.1f%%"),
        "infra_compliance_pct": st.column_config.NumberColumn("Compliance %", format="%.1f%%"),
        "engagement_score": st.column_config.NumberColumn("Engagement Indicator", format="%.1f"),
        "risk_score": st.column_config.NumberColumn("Risk Score", format="%.1f"),
        "risk_level": st.column_config.TextColumn("Risk Level"),
        "open_alerts": "Active Alerts"
    },
    hide_index=True,
    use_container_width=True
)
