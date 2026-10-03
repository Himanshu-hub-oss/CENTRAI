import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import get_db_connection
from ai.discrepancy_engine import AttendanceDiscrepancyEngine

st.set_page_config(page_title="Attendance Discrepancy Engine | Guardian AI", layout="wide")

st.title("⚖️ Module 3 & Discrepancy Engine: Attendance Cross-Check")
st.markdown("Cross-check AI-Estimated Physical Attendance against Centre Submitted Attendance Registers.")

conn = get_db_connection()
centres_df = pd.read_sql_query("SELECT * FROM training_centres", conn)

# Sidebar Filter
c_list = [f"{row['centre_id']} - {row['centre_name']}" for _, row in centres_df.iterrows()]
selected_c_str = st.sidebar.selectbox("Select Target Training Centre", c_list)
cid = selected_c_str.split(" - ")[0]

centre_row = centres_df[centres_df['centre_id'] == cid].iloc[0]

st.markdown(f"### Target Hub: `{centre_row['centre_name']}` ({cid})")

# Inputs for Cross-Check
c1, c2, c3 = st.columns(3)
with c1:
    submitted_att = st.number_input("Submitted Attendance Register Count", min_value=1, max_value=100, value=int(centre_row['registered_trainees']))
with c2:
    ai_detected_att = st.number_input("AI-Detected Physical Trainee Count", min_value=0, max_value=100, value=int(centre_row['present_trainees']))
with c3:
    camera_id = st.selectbox("Select Camera Feed", ["CAM-01 (Main Classroom)", "CAM-02 (Practical Lab)", "CAM-03 (Workshop)"])

engine = AttendanceDiscrepancyEngine()
disc_pct, diff, severity, reason, payload = engine.evaluate_discrepancy(cid, camera_id, submitted_att, ai_detected_att)

st.markdown("---")
st.subheader("📊 Discrepancy Analysis Results")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Submitted Register Count", f"{submitted_att}")
m2.metric("AI Physical Count", f"{ai_detected_att}")
m3.metric("Headcount Difference", f"{diff}", delta_color="inverse")
m4.metric("Discrepancy %", f"{disc_pct}%", delta=f"{severity}", delta_color="inverse")

if severity == "CRITICAL":
    st.error(f"🚨 **CRITICAL DISCREPANCY FLAG**: {reason}")
elif severity == "WARNING":
    st.warning(f"⚠️ **WARNING DISCREPANCY FLAG**: {reason}")
else:
    st.success(f"✅ **NORMAL**: {reason}")

st.markdown("---")
st.subheader("📜 Recent Discrepancy Log History")
history_df = pd.DataFrame([
    {"Timestamp": "2026-10-02 09:15:00", "Submitted": 32, "AI Count": 24, "Diff": 8, "Discrepancy %": "25.0%", "Severity": "CRITICAL", "Status": "Open"},
    {"Timestamp": "2026-10-01 14:30:00", "Submitted": 30, "AI Count": 28, "Diff": 2, "Discrepancy %": "6.7%", "Severity": "NORMAL", "Status": "Verified"},
    {"Timestamp": "2026-09-30 11:00:00", "Submitted": 35, "AI Count": 22, "Diff": 13, "Discrepancy %": "37.1%", "Severity": "CRITICAL", "Status": "Resolved"}
])
st.dataframe(history_df, hide_index=True, use_container_width=True)

conn.close()
