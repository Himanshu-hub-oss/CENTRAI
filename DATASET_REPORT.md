# DATASET REPORT: SkillCentre Guardian AI (SIH 2026 - Problem SIH26245)

## Executive Summary
This report documents the local dataset discovery, structural inspection, module mapping, and AI capabilities for **SkillCentre Guardian AI**, an AI-based real-time monitoring system for government and skill-development training centres.

---

## Bundled Demo Dataset Attribution

A small subset of **10 images** from the **Classroom Student Engagement Dataset** (Roboflow workspace: *ghulams-workspace*, licensed as **Private / Prototype Use**) has been copied to `data/demo_classroom/` to enable the Live Classroom Monitoring demo to function in cloud deployments where the full local dataset (`archive/dataset/images/`) is not accessible.

**Source**: `f:\SIH 26245\archive\dataset\images` → copied to `data/demo_classroom/`  
**Purpose**: Prototype demonstration only — SIH 2026 Hackathon  
**Modification**: No images modified; used as-is for inference demonstration  
**Not for redistribution**; original dataset license applies.

---

## 1. Local Dataset Inventory & Inspection

### Dataset 1: Classroom Student Engagement Dataset (YOLO Format)
- **Location**: `f:\SIH 26245\archive\dataset`
- **Total Images**: 481 `.jpg` images
- **Total Annotation Files**: 481 `.txt` label files (YOLO Normalized format: `class x_center y_center width height`)
- **Total Annotated Bounding Boxes**: 4,603 bounding boxes
- **Target Application**: **Module 3 (Classroom Behaviour Monitoring & Engagement Scoring)** and **Module 1 (Person Detection)**.

#### Class Distribution & Bounding Box Counts:
| Class ID | Class Name | Box Count | Description / Role in Engagement Metric |
|---|---|---|---|
| 0 | `handrise` | 26 | Active Engagement (Weight: +1.5) |
| 1 | `look_forward` | 2,384 | Standard Attention (Weight: +1.0) |
| 2 | `read` | 344 | Active Learning (Weight: +1.0) |
| 3 | `sleep` | 232 | Non-Engaged / Distracted (Weight: -2.0) |
| 4 | `stand` | 60 | Neutral / Active Movement (Weight: 0.0) |
| 5 | `turn_head` | 715 | Mild Distraction (Weight: -0.5) |
| 6 | `using_device` | 522 | Non-Engaged / Off-Task (Weight: -1.5) |
| 7 | `write` | 320 | Active Note-taking (Weight: +1.2) |

#### Split Availability:
- The dataset is provided in a unified structure with `data.yaml` pointing to image folders.
- Validation and Test splits are dynamically partitioned during custom YOLO training (80% Train, 20% Val) to ensure accurate evaluation metrics.

---

### Dataset 2: 2018–2019 Daily Attendance Dataset (CSV)
- **Location**: `f:\SIH 26245\2018-2019_Daily_Attendance_20240429.csv\2018-2019_Daily_Attendance_20240429.csv`
- **Total Rows**: 277,153 daily record rows
- **Total Unique Centres/Schools (`School DBN`)**: 1,583 distinct institutions
- **Date Range**: September 4, 2018 – June 26, 2019 (Full academic year time series)
- **Columns**: `School DBN`, `Date`, `Enrolled`, `Absent`, `Present`, `Released`
- **Data Quality**: 0 missing values, 0 duplicate rows.
- **Target Application**: **Module 4 (Attendance Anomaly Engine)** and **Module 6 (Centre Risk Scoring)**.

#### Derived Features for Anomaly Detection:
- `Attendance_Pct` = `(Present / Enrolled) * 100` (Mean: 89.79%, Std: 9.52%, Min: 0.04%, Max: 100%)
- `7_Day_Moving_Avg_Attendance`
- `Attendance_Drop_7d` = `Previous_7d_Avg - Current_Day_Attendance`
- `Absenteeism_Rate` = `(Absent / Enrolled) * 100`
- Target Labels: Unsupervised anomaly detection via **Isolation Forest** combined with supervised risk thresholding (`Attendance < 50%` or 7-day drop > 25%).

---

## 2. System Module to Dataset Mapping Matrix

| System Module | Input Data Source | Model / Algorithm Used | AI Status | Fallback / Synthetic Flag |
|---|---|---|---|---|
| **Module 1: Person Detection** | Live Webcam / Uploaded Video / Images | Pretrained YOLOv8 / YOLO11 (`yolov8n.pt` person class) | **AI Detected** | Fully operational model |
| **Module 2: Attendance Estimation** | Person Bounding Boxes vs Registered Count | Formula: `(Detected / Enrolled) * 100` | **AI Estimated** | Labeled as "AI-estimated occupancy" |
| **Module 3: Behaviour Detection** | Classroom Engagement Dataset (481 images) | Fine-tuned YOLOv8 Custom Model on 8 classes | **AI Detected** | Fully operational model |
| **Module 4: Attendance Anomaly** | Daily Attendance CSV (277,153 records) | **Isolation Forest** + **Random Forest** Anomaly Classifier | **AI Detected** | Real historical dataset baseline |
| **Module 5: Infrastructure Compliance** | Classroom frames + Officer checklist | YOLOv8 object detection (benches/screens) + Manual checklist | **AI Detected** & **Officer Verified** | Dual-labeling strictly enforced |
| **Module 6: Centre Risk Engine** | Composite of Modules 2, 3, 4, 5 & alerts | Weighted Risk Engine (Anomaly 30%, Infra 25%, Engagement 20%, Alerts 15%, Inspection 10%) | **Rule-Based & AI Synthesis** | Transparent risk breakdown |
| **Module 7 & 8: Alert & Evidence** | Vision frames + Detection metadata | Automatic evidence snapshot generator with bounding boxes | **AI Triggered** | High-res image capture + JSON evidence |
| **Module 9 & 10: Dashboards** | Synthetic PMKVY/DGT Skill Centres + Real CSV stats | Streamlit + Plotly Interactive UI | **Prototype Operational** | Clearly labeled "Synthetic Operational Data" |
| **Module 11: PDF Inspection Report** | Full Centre Profile + Evidence Snapshots | ReportLab PDF Engine | **Automated Engine** | Instant downloadable PDF |

---

## 3. Transparency & Ethical AI Compliance
1. **No Face Recognition**: Person detection strictly uses body bounding box detection (`class 0: person`).
2. **Clear Labeling**: Every metric in the dashboard is explicitly tagged as `AI Detected`, `AI Estimated`, `Rule Based`, `Officer Verified`, or `Synthetic Operational Data`.
3. **Hardware Compatibility**: CPU/GPU auto-detect, zero GPU dependency required, cached model loading.
