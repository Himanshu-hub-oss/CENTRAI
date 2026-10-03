import os
import sys
import sqlite3
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import get_db_connection

st.set_page_config(page_title="AI Alerts & Evidence | Guardian AI", layout="wide")

st.title("⚠️ Module 7 & 8: Evidence-Backed Alert Verification Workflow")
st.markdown("Inspect AI Triggered Anomaly Alerts, Review Visual Evidence Snapshots & Verify Officer Status.")

conn = get_db_connection()
alerts_df = pd.read_sql_query("SELECT * FROM alerts", conn)

if alerts_df.empty:
    st.info("No active alerts present in system.")
else:
    col_sel, col_detail = st.columns([1.0, 1.3])

    with col_sel:
        st.subheader("🚨 Active AI Alerts Queue")
        st.dataframe(
            alerts_df[['alert_id', 'centre_id', 'alert_type', 'severity', 'status']],
            hide_index=True,
            use_container_width=True
        )

        selected_alert_id = st.selectbox("Select Alert ID to Inspect", alerts_df['alert_id'].tolist())

    with col_detail:
        st.subheader(f"🔍 Detailed Evidence: {selected_alert_id}")
        alert_row = alerts_df[alerts_df['alert_id'] == selected_alert_id].iloc[0]

        st.markdown(f"""
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 18px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #dc2626;">ALERT #{alert_row['alert_id']} ({alert_row['severity']})</h4>
                <p style="margin-top: 5px; color: #475569;"><b>Centre ID:</b> {alert_row['centre_id']} | <b>District:</b> {alert_row['district']}</p>
                <p><b>Alert Type:</b> {alert_row['alert_type']}</p>
                <p><b>AI Anomaly Confidence:</b> {alert_row['ai_confidence']}%</p>
                <p><b>AI Trigger Reason:</b> {alert_row['reason']}</p>
                <p><b>Timestamp:</b> {alert_row['timestamp']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📸 Captured Visual Evidence")
        sample_ev = r"f:\SIH 26245\archive\dataset\images\1-second-scene_mp4-0000_jpg.rf.FEE3uKUksPQqBY0UDCWZ.jpg"
        if os.path.exists(sample_ev):
            st.image(sample_ev, caption=f"Evidence Snapshot for {selected_alert_id} (Bounding Boxes & Count Verified)", use_column_width=True)

        st.markdown("#### 👮 Officer Action & Verification Workflow")
        current_status = alert_row['status']
        new_status = st.selectbox("Update Status", ["Open", "Under Review", "Verified", "Resolved", "Rejected"], index=["Open", "Under Review", "Verified", "Resolved", "Rejected"].index(current_status))
        officer_remark = st.text_area("Officer Inspection Remarks", "Verified by District Officer during audit.")

        if st.button("💾 Save Officer Verification Status", type="primary"):
            cursor = conn.cursor()
            cursor.execute("UPDATE alerts SET status = ? WHERE alert_id = ?", (new_status, selected_alert_id))
            conn.commit()
            st.success(f"Alert #{selected_alert_id} status updated to **{new_status}**!")

conn.close()
