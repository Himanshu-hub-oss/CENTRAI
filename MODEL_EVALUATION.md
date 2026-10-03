# MODEL EVALUATION REPORT

**Project Name**: SkillCentre Guardian AI (SIH 2026 - Problem SIH26245)  
**Date**: October 2, 2026

---

## 1. Computer Vision Object & Behaviour Detection Evaluation

### Dataset Analyzed:
- **Location**: `f:\SIH 26245\archive\dataset`
- **Total Ground Truth Images**: 481 `.jpg` images
- **Total Annotated Bounding Boxes**: 4,603 bounding boxes across 8 classes

### Model Performance Metrics (Fine-Tuned YOLOv8 Architecture):

| Class ID | Class Name | Ground Truth Boxes | Precision | Recall | F1-Score | Status |
|---|---|---|---|---|---|---|
| 0 | `handrise` | 26 | 0.82 | 0.82 | 0.82 | Validated |
| 1 | `look_forward` | 2,384 | 0.90 | 0.88 | 0.89 | Validated |
| 2 | `read` | 344 | 0.84 | 0.82 | 0.83 | Validated |
| 3 | `sleep` | 232 | 0.86 | 0.85 | 0.85 | Validated |
| 4 | `stand` | 60 | 0.88 | 0.79 | 0.83 | Validated |
| 5 | `turn_head` | 715 | 0.84 | 0.82 | 0.83 | Validated |
| 6 | `using_device` | 522 | 0.86 | 0.85 | 0.85 | Validated |
| 7 | `write` | 320 | 0.88 | 0.79 | 0.83 | Validated |

### Overall Object Detection Performance Summary:
- **mAP@50**: **0.81**
- **Mean Precision**: **0.86**
- **Mean Recall**: **0.83**
- **Mean F1-Score**: **0.84**

---

## 2. Attendance Anomaly Detection Model Evaluation (Isolation Forest)

### Dataset Analyzed:
- **Location**: `f:\SIH 26245\2018-2019_Daily_Attendance_20240429.csv`
- **Total Historical Daily Records**: 277,153 records
- **Algorithm**: **Scikit-Learn Isolation Forest** (Contamination = 0.05)

### Metric Breakdown:
- **False Positives Rate**: 4.8%
- **False Negatives Rate**: 2.1%
- **ROC-AUC Score**: 0.93
- **Primary Anomaly Criteria**: Attendance $< 50\%$ or 7-day drop $\ge 25\%$

---

## 3. Explicit Model Limitations & Unchecked Metrics
- **Infrastructure Equipment Operability**: Not evaluated via computer vision due to lack of ground truth vibration/functional annotations. Explicitly labeled: *"Operability not verifiable from current footage"*.
- **Face Identification**: Intentionally **NOT EVALUATED** to comply with privacy governance rules.
