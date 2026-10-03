import os
import sys
import cv2
import tempfile
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai.person_detector import PersonDetector
from ai.behaviour_detector import BehaviourDetector
from ai.anomaly_detector import AttendanceAnomalyDetector
from ai.risk_engine import CentreRiskEngine
from backend.database import get_db_connection
from backend.report_generator import InspectionReportGenerator

st.set_page_config(page_title="Live Classroom Monitoring | Guardian AI", layout="wide")

st.title(" Module 1, 2, 3 & Demo Mode: Live Classroom Monitoring")
st.markdown("Real-Time Privacy-Preserving Person Detection, Behaviour Indicator & Automated Risk Audit Workflow.")

# Detect Cloud vs Local environment
IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") is not None or os.environ.get("SERVER_PORT") is not None or os.environ.get("IS_STREAMLIT_CLOUD") is not None or not os.path.exists("C:\\")

# Load AI Engine models once in cache
@st.cache_resource
def load_ai_engines():
    p_detector = PersonDetector()
    b_detector = BehaviourDetector()
    a_detector = AttendanceAnomalyDetector()
    r_engine = CentreRiskEngine()
    rep_gen = InspectionReportGenerator()
    return p_detector, b_detector, a_detector, r_engine, rep_gen

person_detector, behaviour_detector, anomaly_detector, risk_engine, report_generator = load_ai_engines()

# Sidebar: Centre Selection for Live Monitoring
conn = get_db_connection()
centres_df = pd.read_sql_query("SELECT centre_id, centre_name, registered_trainees FROM training_centres", conn)
conn.close()

c_list = [f"{row['centre_id']} - {row['centre_name']}" for _, row in centres_df.iterrows()]
selected_centre_str = st.sidebar.selectbox("Select Target Training Centre", c_list)
selected_cid = selected_centre_str.split(" - ")[0]
selected_reg_cnt = int(centres_df[centres_df['centre_id'] == selected_cid]['registered_trainees'].values[0])

st.sidebar.markdown(f"**Registered Trainees:** {selected_reg_cnt}")
st.sidebar.markdown("---")

# Source Selection - Demo Dataset is default option (1)
source_options = ["Demo Dataset (Bundled Classroom Footage)", "Upload Classroom Image / Video", "Local Camera (Webcam / Feed)"]
source_option = st.radio("Select Video / Frame Source", source_options, index=0, horizontal=True)

input_image = None
frame_status_label = "NOT AVAILABLE"
model_status_badge = "DEMO"
dataset_available = True

if source_option == "Demo Dataset (Bundled Classroom Footage)":
    model_status_badge = "REAL MODEL + DEMO"
    
    # Use relative paths for Streamlit Cloud compatibility
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    demo_dirs = [
        os.path.join(root_dir, "data", "demo_classroom"),
        os.path.join(root_dir, "archive", "dataset", "images"),
        r"f:\SIH 26245\data\demo_classroom",
        r"f:\SIH 26245\archive\dataset\images"
    ]
    
    sample_dir = None
    for d in demo_dirs:
        if os.path.exists(d) and len(os.listdir(d)) > 0:
            sample_dir = d
            break

    if sample_dir and os.path.exists(sample_dir):
        sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if sample_files:
            chosen_file = st.selectbox("Select Demo Dataset Classroom Frame", sample_files)
            sample_path = os.path.join(sample_dir, chosen_file)
            input_image = cv2.imread(sample_path)
            if input_image is not None:
                frame_status_label = f"PROCESSED (DEMO DATASET: {chosen_file})"
        else:
            dataset_available = False
    else:
        dataset_available = False

    if not dataset_available:
        st.error(" **Demo dataset unavailable**. No bundled demo images found in `data/demo_classroom/`. Please use 'Upload Classroom Image / Video'.")

elif source_option == "Upload Classroom Image / Video":
    model_status_badge = "REAL MODEL"
    uploaded_file = st.file_uploader("Upload Classroom Image or Video File (MP4/AVI/MOV/JPG/PNG)", type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'])
    
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(('mp4', 'avi', 'mov')):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())
            tfile.close()
            
            cap = cv2.VideoCapture(tfile.name)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames > 0:
                frame_slider = st.slider("Video Timeline Frame Control (Sampled Frame)", 0, max(0, total_frames - 1), 0)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_slider)
                ret, frame = cap.read()
                if ret and frame is not None:
                    input_image = frame
                    frame_status_label = f"PROCESSED (UPLOADED VIDEO FRAME {frame_slider}/{total_frames})"
            cap.release()
            try:
                os.unlink(tfile.name)
            except Exception:
                pass
        else:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            input_image = cv2.imdecode(file_bytes, 1)
            if input_image is not None:
                frame_status_label = "PROCESSED (UPLOADED IMAGE)"

elif source_option == "Local Camera (Webcam / Feed)":
    model_status_badge = "LOCAL ONLY"
    st.info(" Local Camera mode captures frames directly from hardware webcam.")
    
    if IS_CLOUD:
        st.warning(" **Local Camera Unavailable on Cloud Deployment**. Local hardware cameras cannot be accessed remotely from cloud servers. Please use **'Demo Dataset (Bundled Classroom Footage)'** or **'Upload Classroom Image / Video'**.")
    else:
        camera_img = st.camera_input("Take Live Classroom Photo")
        if camera_img is not None:
            bytes_data = camera_img.getvalue()
            file_bytes = np.asarray(bytearray(bytes_data), dtype=np.uint8)
            input_image = cv2.imdecode(file_bytes, 1)
            if input_image is not None:
                frame_status_label = "PROCESSED (LIVE CAMERA)"

st.markdown("---")

# Execution & Display
if input_image is not None:
    col1, col2 = st.columns([1.3, 1.0])

    with col1:
        st.subheader(" AI Computer Vision Real-Time Feed")
        st.markdown(f"Status: `<span style='color: green; font-weight: bold;'>{frame_status_label}</span>` | Model Status: `<span style='background-color: #0284c7; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>{model_status_badge}</span>`", unsafe_allow_html=True)
        st.write("")

        # 1. Person Detection Pipeline
        annotated_person_img, detected_count, conf_pct, detections, fps = person_detector.detect(input_image)
        
        # 2. Behaviour Detection Pipeline
        annotated_behaviour_img, b_counts, engagement_score, b_dets = behaviour_detector.analyze(input_image)

        # Tabbed visual outputs
        v_tab1, v_tab2 = st.tabs(["Person Detection & Occupancy", "Classroom Behaviour Indicator"])
        
        with v_tab1:
            st.image(cv2.cvtColor(annotated_person_img, cv2.COLOR_BGR2RGB), use_column_width=True)
            st.caption(" *Privacy-Preserving Bounding Box Detection. Zero face recognition or biometric storage.*")
            
        with v_tab2:
            st.image(cv2.cvtColor(annotated_behaviour_img, cv2.COLOR_BGR2RGB), use_column_width=True)
            st.caption(" *Classroom Engagement Indicator: Multi-class action bounding box detection.*")

    with col2:
        st.subheader(" Live AI Analytical Decision Support")
        
        # Attendance Estimation Formula
        estimated_att_pct = round((detected_count / selected_reg_cnt) * 100, 1) if selected_reg_cnt > 0 else 0.0
        
        att_status = "NORMAL" if estimated_att_pct >= 75.0 else ("WARNING" if estimated_att_pct >= 50.0 else "CRITICAL")
        att_color = "#16a34a" if att_status == "NORMAL" else ("#d97706" if att_status == "WARNING" else "#dc2626")

        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #0f172a;">Module 2: Attendance Estimation</h4>
                <p style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">Label: <b>AI-Estimated Classroom Occupancy</b></p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <div><b>Registered:</b> {selected_reg_cnt}</div>
                    <div><b>AI Detected:</b> {detected_count}</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {att_color};">{estimated_att_pct}% ({att_status})</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Behaviour Breakdown Table
        st.markdown(f"**Module 3: Classroom Engagement Indicator: `{engagement_score} / 100`**")
        b_df = pd.DataFrame(list(b_counts.items()), columns=['Behaviour Class', 'Detected Count'])
        st.dataframe(b_df, hide_index=True, use_container_width=True)

        # 3. Attendance Anomaly Module Call
        is_anom, anom_score, anom_reason = anomaly_detector.detect_anomaly(estimated_att_pct, selected_reg_cnt, historical_7d_avg=88.0)
        
        st.markdown("---")
        st.subheader(" Module 4: Anomaly Detection Engine")
        if is_anom:
            st.error(f"**ANOMALY DETECTED (Score: {anom_score})**\n\n{anom_reason}")
        else:
            st.success(f"**NORMAL BASELINE (Score: {anom_score})**\n\n{anom_reason}")

        # 4. Centre Risk Calculation & Alert Trigger
        risk_score, risk_lvl, bdown, risk_reasons = risk_engine.calculate_risk(
            attendance_pct=estimated_att_pct,
            infra_compliance_pct=85.0,
            engagement_score=engagement_score,
            open_alert_count=1 if is_anom else 0,
            days_since_last_inspection=20
        )

        st.markdown("---")
        st.subheader(" Module 6 & 11: End-to-End Live Audit & Report")
        st.markdown(f"Calculated Centre Risk Level: **:{'red' if risk_lvl=='HIGH RISK' else 'green'}[{risk_lvl}]** (Score: {risk_score})")

        if st.button(" Generate Live Officer PDF Inspection Report", type="primary"):
            os.makedirs("evidence", exist_ok=True)
            evidence_path = os.path.join("evidence", f"Evidence_{selected_cid}_{int(np.random.randint(1000,9999))}.jpg")
            cv2.imwrite(evidence_path, annotated_person_img)

            centre_dict = {
                'centre_id': selected_cid,
                'centre_name': selected_centre_str.split(" - ")[1],
                'state': 'Madhya Pradesh',
                'district': selected_cid.split("-")[1],
                'course': 'Solar PV Technician',
                'registered_trainees': selected_reg_cnt,
                'present_trainees': detected_count,
                'attendance_pct': estimated_att_pct,
                'infra_compliance_pct': 85.0,
                'risk_score': risk_score,
                'risk_level': risk_lvl
            }
            alert_dict = [{'alert_id': 'AL-LIVE-99', 'alert_type': 'Live Attendance Anomaly', 'severity': 'CRITICAL' if is_anom else 'NORMAL', 'ai_confidence': conf_pct, 'reason': anom_reason}]

            pdf_out = report_generator.generate_pdf(centre_dict, [], alert_dict, evidence_img_path=evidence_path)
            
            with open(pdf_out, "rb") as f:
                st.download_button(" Download Official Inspection PDF Report", f, file_name=os.path.basename(pdf_out), mime="application/pdf")
            st.success("Official PDF Inspection Report Generated with AI Evidence Snapshot!")

else:
    # State when NO video or image source is loaded
    status_msg = "Demo dataset unavailable" if not dataset_available else "Please upload a classroom video (MP4/AVI/MOV), an image, or select a demo dataset frame above."
    st.markdown(f"""
        <div style="background-color: #1e293b; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #38bdf8;">📹 Video / Camera Feed: NOT AVAILABLE</h3>
                    <p style="color: #94a3b8; margin-top: 5px;">{status_msg}</p>
                </div>
                <div>
                    <span style="background-color: #334155; color: #cbd5e1; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">STATUS: WAITING FOR VIDEO</span>
                </div>
            </div>
            <hr style="border-color: #334155; margin: 15px 0;">
            <div style="display: flex; gap: 40px;">
                <div><span style="color: #94a3b8;">AI Trainee Count:</span> <b style="color: #f1f5f9;">N/A</b></div>
                <div><span style="color: #94a3b8;">Attendance Estimate:</span> <b style="color: #f1f5f9;">N/A</b></div>
                <div><span style="color: #94a3b8;">Engagement Score:</span> <b style="color: #f1f5f9;">N/A</b></div>
                <div><span style="color: #94a3b8;">Model Status:</span> <b style="color: #38bdf8;">NOT AVAILABLE</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
