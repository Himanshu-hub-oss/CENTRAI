import os
import sys
import numpy as np
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ai.low_bandwidth_manager import LowBandwidthManager, CameraQualityAssessor

st.set_page_config(page_title="Low Bandwidth & Camera Quality | Guardian AI", layout="wide")

st.title(" Module 9: Low-Bandwidth Mode & Camera Quality Assessment")
st.markdown("Rural & Semi-Urban Deployment Constraints Management.")

st.sidebar.markdown("### Deployment Settings")
lbm_enabled = st.sidebar.toggle("Enable Low Bandwidth Mode", value=True)
sample_rate = st.sidebar.slider("Frame Sampling Interval (1 in N)", min_value=1, max_value=10, value=3)

lbm = LowBandwidthManager(mode_enabled=lbm_enabled, sample_interval=sample_rate)

# Simulate 30 frames
for i in range(30):
    lbm.process_frame_decision(np.zeros((360, 640, 3), dtype=np.uint8), i)

stats = lbm.get_bandwidth_stats()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Low Bandwidth Mode", "ACTIVE" if lbm_enabled else "OFF")
c2.metric("Frames Processed", f"{stats['frames_processed']}")
c3.metric("Frames Skipped", f"{stats['frames_skipped']}")
c4.metric("Est Data Reduction", f"{stats['skip_percentage']}% (~{stats['est_data_saved_mb']} MB)")

st.markdown("---")
st.subheader(" Camera Quality Diagnostics")

sample_img_path = r"f:\SIH 26245\archive\dataset\images\1-second-scene_mp4-0000_jpg.rf.FEE3uKUksPQqBY0UDCWZ.jpg"
if os.path.exists(sample_img_path):
    import cv2
    img = cv2.imread(sample_img_path)
    assessor = CameraQualityAssessor()
    status, metrics, reasons = assessor.assess_quality(img)

    q1, q2 = st.columns([1.0, 1.2])
    with q1:
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="Inspected Feed", use_column_width=True)
    with q2:
        st.markdown(f"### Camera Status: **:{'green' if status=='GOOD' else 'orange'}[{status}]**")
        st.json(metrics)
        st.markdown("**Diagnostics & Recommendations:**")
        for r in reasons:
            st.write(f"- {r}")

st.caption(" *Data reduction numbers reflect architecture-level estimated savings calculated from frame sampling and downsampling.*")
