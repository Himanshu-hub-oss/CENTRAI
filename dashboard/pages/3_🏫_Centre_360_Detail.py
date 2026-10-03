import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import get_db_connection

st.set_page_config(page_title="Centre 360 Profile | Guardian AI", layout="wide")

st.title("🏫 Module 10: Centre 360-Degree Comprehensive Profile")

conn = get_db_connection()
centres_df = pd.read_sql_query("SELECT * FROM training_centres", conn)

c_options = [f"{row['centre_id']} - {row['centre_name']} ({row['state']})" for _, row in centres_df.iterrows()]
selected_str = st.selectbox("Select Training Centre to Inspect", c_options)
cid = selected_str.split(" - ")[0]

centre_row = centres_df[centres_df['centre_id'] == cid].iloc[0]

# Query sub-tables
att_history_df = pd.read_sql_query("SELECT * FROM attendance_logs WHERE centre_id = ? ORDER BY date ASC", conn, params=(cid,))
comp_df = pd.read_sql_query("SELECT * FROM compliance_items WHERE centre_id = ?", conn, params=(cid,))
alerts_df = pd.read_sql_query("SELECT * FROM alerts WHERE centre_id = ?", conn, params=(cid,))
conn.close()

# Overview Header Cards
r_lvl = centre_row['risk_level']
r_color = "#dc2626" if r_lvl == "HIGH RISK" else ("#d97706" if r_lvl == "MEDIUM RISK" else "#16a34a")

st.markdown(f"""
    <div style="background-color: #f8fafc; border-radius: 12px; padding: 20px; border: 1px solid #cbd5e1; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #0f172a;">{centre_row['centre_name']}</h2>
                <p style="color: #64748b; margin-top: 4px;"><b>Centre ID:</b> {centre_row['centre_id']} | <b>State:</b> {centre_row['state']} | <b>District:</b> {centre_row['district']} | <b>Course:</b> {centre_row['course']}</p>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.4rem; font-weight: 700; color: {r_color}; border: 2px solid {r_color}; padding: 6px 14px; border-radius: 8px;">{r_lvl}</span>
                <p style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">Risk Score: <b>{centre_row['risk_score']} / 100</b></p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Tabs
t1, t2, t3, t4 = st.tabs(["Overview & Trends", "Infrastructure Compliance Checklist", "AI Alerts History", "Audit History"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📈 14-Day Attendance Trend")
        if not att_history_df.empty:
            fig_line = px.line(att_history_df, x="date", y="attendance_pct", markers=True, title="Daily Attendance Occupancy %")
            fig_line.add_hline(y=75, line_dash="dash", line_color="orange", annotation_text="Target 75%")
            fig_line.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Critical 50%")
            st.plotly_chart(fig_line, use_container_width=True)
    with col_b:
        st.subheader("🎯 Sub-Module Performance Scores")
        score_df = pd.DataFrame([
            {"Metric": "AI Attendance %", "Score": centre_row['attendance_pct']},
            {"Metric": "Infra Compliance %", "Score": centre_row['infra_compliance_pct']},
            {"Metric": "Engagement Indicator", "Score": centre_row['engagement_score']}
        ])
        fig_bar = px.bar(score_df, x="Metric", y="Score", color="Metric", text="Score", title="Centre Performance Profile")
        st.plotly_chart(fig_bar, use_container_width=True)

with t2:
    st.subheader("📋 Module 5: Infrastructure & Safety Compliance Checklist")
    st.markdown("Explicit Dual Labeling: **AI Detected** vs **Officer Verified**")
    st.dataframe(
        comp_df[['item_name', 'category', 'ai_detected_status', 'officer_verified_status', 'remarks']],
        hide_index=True,
        use_container_width=True
    )

with t3:
    st.subheader("🚨 Module 7 & 8: AI Alerts & Evidence Snapshots")
    if not alerts_df.empty:
        st.dataframe(
            alerts_df[['alert_id', 'timestamp', 'alert_type', 'severity', 'ai_confidence', 'reason', 'status']],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No active alerts logged for this centre.")

with t4:
    st.subheader("🗓️ Inspection History")
    st.write(f"**Last Inspection Date:** {centre_row['last_inspection_date']}")
    st.write(f"**Operational Status:** Active Monitored")
