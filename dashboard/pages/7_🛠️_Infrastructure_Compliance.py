import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import get_db_connection
from ai.infra_detector import InfrastructureDetector

st.set_page_config(page_title="Infrastructure Compliance | Guardian AI", layout="wide")

st.title("🛠️ Module 5: Infrastructure & Equipment Compliance Inventory")
st.markdown("Automated Inventory Verification & Apparent Operability Assessment.")

conn = get_db_connection()
centres_df = pd.read_sql_query("SELECT * FROM training_centres", conn)

c_list = [f"{row['centre_id']} - {row['centre_name']}" for _, row in centres_df.iterrows()]
selected_c_str = st.sidebar.selectbox("Select Training Centre", c_list)
cid = selected_c_str.split(" - ")[0]

st.subheader(f"Sanctioned Equipment Inventory — `{cid}`")

# Run Infrastructure Detector
sample_img = r"f:\SIH 26245\archive\dataset\images\1-second-scene_mp4-0000_jpg.rf.FEE3uKUksPQqBY0UDCWZ.jpg"
detector = InfrastructureDetector()

if os.path.exists(sample_img):
    annotated_frame, report, score = detector.detect_inventory(sample_img)
    
    col_img, col_rep = st.columns([1.2, 1.0])
    with col_img:
        st.subheader("📷 Computer Vision Equipment Bounding Box Feed")
        st.image(annotated_frame, channels="BGR", use_column_width=True)
    
    with col_rep:
        st.subheader(f"📊 Compliance Score: `{score}%`")
        rep_df = pd.DataFrame(report)
        st.dataframe(
            rep_df[['item_name', 'expected_qty', 'detected_qty', 'status', 'presence_label', 'operability_status']],
            column_config={
                "item_name": "Equipment Item",
                "expected_qty": "Expected Qty",
                "detected_qty": "Detected Qty",
                "status": "Status",
                "presence_label": "Presence",
                "operability_status": "Operability Assessment"
            },
            hide_index=True,
            use_container_width=True
        )

st.info("ℹ️ **Compliance Rule**: Equipment operability is strictly labeled *'Operability not verifiable from current footage'* unless physical sensor verification is available.")

conn.close()
