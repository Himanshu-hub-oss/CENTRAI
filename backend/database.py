import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_PATH = 'backend/guardian.db'
CSV_ATTENDANCE_PATH = r'f:\SIH 26245\2018-2019_Daily_Attendance_20240429.csv\2018-2019_Daily_Attendance_20240429.csv'

STATES_DISTRICTS = {
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Rewa"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"]
}

COURSES = ["Solar PV Technician", "CNC Machine Operator", "Data Entry Operator", "Electrician", "Automotive Service Technician"]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("[Database] Initializing SQLite database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Centres table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_centres (
            centre_id TEXT PRIMARY KEY,
            centre_name TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            course TEXT NOT NULL,
            registered_trainees INTEGER NOT NULL,
            present_trainees INTEGER NOT NULL,
            attendance_pct REAL NOT NULL,
            infra_compliance_pct REAL NOT NULL,
            engagement_score REAL NOT NULL,
            open_alerts INTEGER DEFAULT 0,
            risk_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            last_inspection_date TEXT NOT NULL,
            data_flag TEXT DEFAULT 'Prototype / Synthetic Operational Data'
        )
    ''')

    # 2. Daily Attendance Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            centre_id TEXT NOT NULL,
            date TEXT NOT NULL,
            enrolled INTEGER NOT NULL,
            present INTEGER NOT NULL,
            attendance_pct REAL NOT NULL,
            FOREIGN KEY (centre_id) REFERENCES training_centres (centre_id)
        )
    ''')

    # 3. Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            centre_id TEXT NOT NULL,
            district TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            ai_confidence REAL NOT NULL,
            reason TEXT NOT NULL,
            evidence_image_path TEXT,
            status TEXT DEFAULT 'Open',
            data_flag TEXT DEFAULT 'Prototype / Synthetic Operational Data',
            FOREIGN KEY (centre_id) REFERENCES training_centres (centre_id)
        )
    ''')

    # 4. Infrastructure Compliance Checklist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            centre_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            ai_detected_status TEXT, -- AI Detected
            officer_verified_status TEXT, -- Officer Verified
            remarks TEXT,
            FOREIGN KEY (centre_id) REFERENCES training_centres (centre_id)
        )
    ''')

    conn.commit()
    conn.close()

def seed_database_with_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM training_centres")
    if cursor.fetchone()[0] > 0:
        print("[Database] Database already populated with records.")
        conn.close()
        return

    print("[Database] Seeding 35 realistic Training Centres across Indian States...")

    np.random.seed(42)
    centre_index = 101

    for state, districts in STATES_DISTRICTS.items():
        for dist in districts:
            c_id = f"TC-{dist[:3].upper()}-{centre_index}"
            c_name = f"PMKVY Skill Development Hub ({dist})"
            course = np.random.choice(COURSES)
            reg = int(np.random.choice([25, 30, 35, 40]))
            
            # Create a mix of normal (80%) and high risk (20%) centres for rich dashboard visualization
            is_risky = (centre_index % 5 == 0)
            if is_risky:
                pres = int(reg * np.random.uniform(0.35, 0.52))
                infra = round(np.random.uniform(45.0, 68.0), 1)
                eng = round(np.random.uniform(40.0, 58.0), 1)
                alerts_cnt = np.random.randint(2, 5)
                risk_lvl = "HIGH RISK"
                risk_score = round(np.random.uniform(68.0, 89.0), 1)
                insp_days = np.random.randint(45, 90)
            else:
                pres = int(reg * np.random.uniform(0.76, 0.95))
                infra = round(np.random.uniform(82.0, 98.0), 1)
                eng = round(np.random.uniform(72.0, 94.0), 1)
                alerts_cnt = np.random.choice([0, 1], p=[0.7, 0.3])
                risk_lvl = "LOW RISK" if alerts_cnt == 0 else "MEDIUM RISK"
                risk_score = round(np.random.uniform(12.0, 42.0), 1)
                insp_days = np.random.randint(5, 30)

            att_pct = round((pres / reg) * 100, 1)
            last_insp = (datetime.now() - timedelta(days=insp_days)).strftime("%Y-%m-%d")

            cursor.execute('''
                INSERT INTO training_centres (
                    centre_id, centre_name, state, district, course,
                    registered_trainees, present_trainees, attendance_pct,
                    infra_compliance_pct, engagement_score, open_alerts,
                    risk_score, risk_level, last_inspection_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (c_id, c_name, state, dist, course, reg, pres, att_pct, infra, eng, alerts_cnt, risk_score, risk_lvl, last_insp))

            # Seed 14 days of historical attendance for trends
            for i in range(14, 0, -1):
                d_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                if is_risky and i <= 3:
                    # Drop in last 3 days
                    p_hist = int(reg * np.random.uniform(0.4, 0.5))
                else:
                    p_hist = int(reg * np.random.uniform(0.75, 0.95))
                a_pct_hist = round((p_hist / reg) * 100, 1)
                cursor.execute('''
                    INSERT INTO attendance_logs (centre_id, date, enrolled, present, attendance_pct)
                    VALUES (?, ?, ?, ?, ?)
                ''', (c_id, d_str, reg, p_hist, a_pct_hist))

            # Seed Compliance Checklist items with explicit AI Detected vs Officer Verified labels
            items = [
                ("Computer Lab PCs Working", "Equipment", "AI Detected", "Available", "All 15 PCs operational"),
                ("CCTV Stream Active", "Safety", "AI Detected", "Available", "Classroom feed live"),
                ("Seating Arrangement", "Classroom", "AI Detected", "Available", "Benches adequate"),
                ("Fire Extinguisher Installed", "Safety", "Officer Verified", "Available", "Valid till Dec 2026"),
                ("Biometric Device Operational", "Attendance", "Officer Verified", "Missing" if is_risky else "Available", "Device sensor maintenance required" if is_risky else "Active"),
                ("First Aid Kit", "Safety", "Officer Verified", "Needs Inspection" if is_risky else "Available", "Check contents")
            ]
            for iname, cat, aidet, offver, rem in items:
                cursor.execute('''
                    INSERT INTO compliance_items (centre_id, item_name, category, ai_detected_status, officer_verified_status, remarks)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (c_id, iname, cat, aidet, offver, rem))

            # Seed AI Alerts for risky centres
            if alerts_cnt > 0:
                for a_idx in range(alerts_cnt):
                    al_id = f"AL-{c_id[-3:]}-{100 + a_idx}"
                    al_type = "Attendance Anomaly" if a_idx == 0 else "Low Engagement Alert"
                    sev = "CRITICAL" if is_risky else "WARNING"
                    reason = f"Attendance dropped to {att_pct}% (Significant deviation from 88% historical baseline)." if a_idx == 0 else "Classroom engagement score dropped below 55%."
                    ts = (datetime.now() - timedelta(hours=a_idx * 6 + 2)).strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                        INSERT INTO alerts (alert_id, centre_id, district, timestamp, alert_type, severity, ai_confidence, reason, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (al_id, c_id, dist, ts, al_type, sev, round(np.random.uniform(91.0, 97.5), 1), reason, 'Open'))

            centre_index += 1

    conn.commit()
    conn.close()
    print("[Database] Database seeding complete with 35 Centres & Alert records.")

if __name__ == "__main__":
    seed_database_with_data()
