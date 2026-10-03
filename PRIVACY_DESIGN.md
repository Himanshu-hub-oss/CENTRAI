# PRIVACY & DATA GOVERNANCE DESIGN DOCUMENTATION

**System**: SkillCentre Guardian AI (SIH26245)  
**Privacy Status**: Privacy-Preserving Mode **ON** by Default

---

## 1. Core Privacy Architecture & Directives

SkillCentre Guardian AI is designed with strict adherence to **Privacy-by-Design** principles. It monitors training centre attendance and classroom engagement **without identifying individual trainees**.

```
CAMERA FEED ──► Person Box Detection (class 0) ──► Aggregate Count ──► DISCARD FRAME
                    │
                    └──► Facial Recognition: DISABLED
                    └──► Biometric Storage: NONE
                    └──► Aadhaar / PII Linkage: ZERO
```

---

## 2. Privacy Matrix: What Is Detected vs What Is NOT Identified

| Category | What IS Detected / Estimated | What IS NOT Identified | Technical Enforcement |
|---|---|---|---|
| **Presence** | Anonymous Person Bounding Box | Name, Face, Trainee ID | YOLO class 0 person detector only |
| **Occupancy** | Total Trainee Headcount | Aadhaar, Phone Number, Biometrics | Aggregate count calculation |
| **Behaviour** | Generic Action (e.g. `look_forward`, `read`) | Individual Attentiveness Profile | Anonymous region bounding box |
| **Storage** | Event Evidence Snapshots (Alerts only) | Continuous Raw Video Stream | Event-driven image logging |

---

## 3. Configurable Privacy Modes

- **Privacy Mode = ON (Default)**:
  - All person bounding boxes labeled generically as `Trainee #1`, `Trainee #2`.
  - Facial landmarks blur overlay active during live visual streaming.
  - Zero PII stored in SQLite database.
- **Privacy Mode = OFF (Debug Only)**:
  - Raw frame view for inspecting camera calibration.
