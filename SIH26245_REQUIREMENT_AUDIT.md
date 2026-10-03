# SIH26245 OFFICIAL REQUIREMENT AUDIT

**Project Name**: SkillCentre Guardian AI  
**Problem Statement**: SIH26245 - AI-Based Real-Time Monitoring of Training Centres for Attendance and Infrastructure Compliance  
**Date**: October 2, 2026

---

## Requirement Compliance Matrix

| # | Requirement | Implemented? | Real / Rule / Demo | File / Function | Evidence / Status | Missing Work / Gaps |
|---|---|---|---|---|---|---|
| 1 | Process live or periodic camera feeds | **PARTIAL** | Real CV & Periodic | `dashboard/pages/2_📹_Live_Classroom_Monitoring.py` | Handles image upload, video, live camera input | Frame sampling, quality assessment & low-bandwidth frame skipping need formal integration |
| 2 | Estimate actual physical attendance from video | **YES** | Real AI | `ai/person_detector.py` -> `PersonDetector.detect()` | YOLOv8 person detection (`class 0`) with count | Needs discrepancy calculation against submitted attendance records |
| 3 | Cross-check AI-estimated vs submitted attendance | **PARTIAL** | Rule-Based / Synth | `dashboard/app.py`, `ai/anomaly_detector.py` | Shows attendance % vs 50% threshold | Dedicated Attendance Discrepancy Engine comparing AI count vs centre submitted register count |
| 4 | Detect presence/absence of approved infrastructure items | **PARTIAL** | Rule + Demo | `backend/database.py` (`compliance_items`) | Dual-labeled items in DB (AI Detected vs Officer Verified) | Needs vision-based inventory detection module (`infra_detector.py`) for desks/computers/machinery |
| 5 | Detect apparent equipment operability | **PARTIAL** | Rule / State | `backend/database.py` | Stores operational status | Needs explicit status: "PRESENT", "APPARENTLY OPERATIONAL", or "Operability not verifiable from footage" |
| 6 | Flag attendance discrepancies | **YES** | Real AI + Rule | `ai/anomaly_detector.py` -> `detect_anomaly()` | Isolation Forest anomaly detection + drop flags | Needs structured Discrepancy Engine output (Submitted, AI Count, Diff, Discrepancy %) |
| 7 | Flag missing/non-functional infrastructure | **YES** | Rule + DB | `backend/database.py`, `dashboard/pages/3_🏫_Centre_360_Detail.py` | Checklist status in Centre 360 profile | Needs automated alert triggers for missing critical items |
| 8 | Display alerts on monitoring dashboard | **YES** | Real UI + DB | `dashboard/pages/4_⚠️_AI_Alerts_&_Evidence.py` | Interactive queue with status update workflow | Add explicit event-driven alert types (`ATTENDANCE_DISCREPANCY`, `MISSING_EQUIPMENT`, `LOW_BANDWIDTH_EVENT`) |
| 9 | Realistic bandwidth & camera-quality constraints | **PARTIAL** | Architecture | `README.md` | Local CPU friendly YOLO inference | Needs Low Bandwidth Mode toggle, frame downsampling, and Camera Quality Assessor (`GOOD`/`FAIR`/`POOR`) |
| 10 | Preserve trainee privacy using aggregate presence | **YES** | Real AI Design | `ai/person_detector.py` | Bounding box detection on `class 0: person` only. Zero facial ID. | Add dedicated Privacy & Governance dashboard tab with toggle (`Privacy Mode = ON`) |
| 11 | Working demonstration on sample/simulated footage | **YES** | Real + Demo | `dashboard/pages/2_📹_Live_Classroom_Monitoring.py` | Uses local dataset sample images & live webcam | Standardize explicit "DEMO / SIMULATED" badge on all non-real AI outputs |
| 12 | Attendance-discrepancy & compliance dashboard | **YES** | Real UI | `dashboard/app.py`, `dashboard/pages/` | Multi-page Streamlit dashboard | Create dedicated "Attendance Discrepancy" and "Low Bandwidth" pages |
| 13 | Privacy-preserving design explanation | **YES** | Text / Report | `DATASET_REPORT.md`, `README.md` | Documents privacy rules | Needs formal standalone `PRIVACY_DESIGN.md` document & dashboard UI section |
| 14 | False-positive / false-negative accuracy assessment | **NO** | Not Evaluated | N/A | Missing precision/recall assessment on local datasets | Needs `MODEL_EVALUATION.md` calculating mAP, precision, recall on ground truth labels |
| 15 | Low-bandwidth deployment mode | **NO** | Architecture | N/A | Missing low-bandwidth mode toggle & stats | Needs `LOW_BANDWIDTH_DESIGN.md` & Low Bandwidth Manager module |

---

## 🎯 Actionable Engineering Roadmap for Phase 2 Implementation

1. **`ai/infra_detector.py`**: Vision & rule-based infrastructure inventory detector (computers, workbenches, seating, machines) with strict state labeling (`PRESENT`, `APPARENTLY OPERATIONAL`, `NOT VERIFIABLE`).
2. **`ai/discrepancy_engine.py`**: Attendance Discrepancy Engine comparing Submitted Register Count vs AI Detected Count ($Discrepancy \% = |Submitted - AI| / Submitted \times 100$).
3. **`ai/low_bandwidth_manager.py`**: Low Bandwidth & Camera Quality Engine (Frame downsampling, blur/brightness evaluation, skipped frame counters).
4. **`ai/model_evaluator.py`**: Evaluates model performance on local dataset annotations producing precision, recall, mAP, and confusion matrix.
5. **Dashboard Extensions**:
   - Navigation & System Status Bar (Camera, AI Detection, Attendance Data, Infrastructure, Alerts, DB).
   - Dedicated Pages for Discrepancy, Infrastructure Compliance, Privacy & Governance, Low Bandwidth, and Model Evaluation.
6. **Documentation Deliverables**:
   - `SIH26245_REQUIREMENT_AUDIT.md`
   - `MODEL_EVALUATION.md`
   - `PRIVACY_DESIGN.md`
   - `LOW_BANDWIDTH_DESIGN.md`
   - `INTEGRATION_TEST_REPORT.md`
