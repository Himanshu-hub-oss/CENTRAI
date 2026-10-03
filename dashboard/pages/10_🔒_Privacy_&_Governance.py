import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

st.set_page_config(page_title="Privacy & Governance | Guardian AI", layout="wide")

st.title(" Privacy & Data Governance Architecture")
st.markdown("Privacy-by-Design Compliance for Skill Development Training Centre Monitoring.")

st.sidebar.markdown("### Privacy Controls")
priv_mode = st.sidebar.toggle("Privacy Mode Enabled", value=True)

if priv_mode:
    st.success(" **Privacy Mode = ON (ACTIVE)**: All person detection outputs use anonymous bounding box coordinates (`Trainee #1`, `Trainee #2`). Zero facial recognition, biometric storage, or Aadhaar linkage.")
else:
    st.warning(" **Privacy Mode = OFF (DEBUG MODE)**: Raw video feed view active for camera angle calibration.")

st.markdown("---")
st.subheader(" Data Governance Matrix")

st.markdown("""
| Feature Category | What IS Detected / Processed | What IS NOT Identified | Technical Enforcement |
|---|---|---|---|
| **Presence** | Anonymous Person Bounding Box | Name, Face, Trainee ID | YOLO class 0 person detector only |
| **Occupancy** | Total Trainee Headcount | Aadhaar, Phone Number, Biometrics | Aggregate count calculation |
| **Behaviour** | Generic Action (e.g. `look_forward`, `read`) | Individual Attentiveness Profile | Anonymous region bounding box |
| **Storage** | Event Evidence Snapshots (Alerts only) | Continuous Raw Video Stream | Event-driven image logging |
""")

st.markdown("---")
st.subheader(" Constitutional & Ethical Compliance Checklist")
st.checkbox("Zero Biometric Facial Recognition", value=True, disabled=True)
st.checkbox("Zero Aadhaar or Personal Identity Storage", value=True, disabled=True)
st.checkbox("Edge-Local Processing & Frame Discarding", value=True, disabled=True)
st.checkbox("Event-Driven Evidence Snapshots Only", value=True, disabled=True)
