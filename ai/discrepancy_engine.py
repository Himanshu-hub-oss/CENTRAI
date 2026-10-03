from datetime import datetime

class AttendanceDiscrepancyEngine:
    def __init__(self, warning_thresh_pct=15.0, critical_thresh_pct=25.0):
        """
        Attendance Discrepancy Engine comparing Submitted Training Centre Attendance Register
        against Physical AI-Detected Occupancy.
        
        Formula:
        Difference = |Submitted Attendance - AI Detected Attendance|
        Discrepancy % = (Difference / Submitted Attendance) * 100
        """
        self.warning_thresh_pct = warning_thresh_pct
        self.critical_thresh_pct = critical_thresh_pct

    def evaluate_discrepancy(self, centre_id, camera_id, submitted_count, ai_detected_count):
        """
        Evaluates physical discrepancy and generates structured event payload.
        Returns:
            discrepancy_pct (float): Calculated percentage difference
            difference (int): Submitted - AI Detected
            severity (str): NORMAL | WARNING | CRITICAL
            reason (str): Transparent plain-text explanation
            alert_payload (dict): Structured event payload for dashboard & evidence system
        """
        submitted_count = max(1, int(submitted_count))
        ai_detected_count = max(0, int(ai_detected_count))
        
        difference = submitted_count - ai_detected_count
        discrepancy_pct = round((abs(difference) / submitted_count) * 100.0, 1)

        if discrepancy_pct >= self.critical_thresh_pct or difference >= 10:
            severity = "CRITICAL"
        elif discrepancy_pct >= self.warning_thresh_pct or difference >= 5:
            severity = "WARNING"
        else:
            severity = "NORMAL"

        # Build transparent explainable reason
        if difference > 0:
            reason = f"Ghost Attendance Flagged: Centre submitted register ({submitted_count}) exceeds AI detected physical presence ({ai_detected_count}) by {difference} trainees ({discrepancy_pct}% discrepancy)."
        elif difference < 0:
            reason = f"Overcrowding Flagged: AI detected presence ({ai_detected_count}) exceeds registered submission ({submitted_count}) by {abs(difference)} trainees."
        else:
            reason = f"Attendance Verified: Centre submitted count matches AI physical detection exactly ({submitted_count} trainees)."

        alert_payload = {
            "alert_id": f"AL-DISC-{centre_id[-3:]}-{int(datetime.now().timestamp()) % 10000}",
            "alert_type": "ATTENDANCE_DISCREPANCY",
            "centre_id": centre_id,
            "camera_id": camera_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "submitted_count": submitted_count,
            "ai_detected_count": ai_detected_count,
            "difference": difference,
            "discrepancy_pct": discrepancy_pct,
            "severity": severity,
            "reason": reason,
            "status": "Open",
            "data_flag": "AI Calculated Discrepancy"
        }

        return discrepancy_pct, difference, severity, reason, alert_payload

if __name__ == "__main__":
    engine = AttendanceDiscrepancyEngine()
    disc_pct, diff, sev, reason, payload = engine.evaluate_discrepancy("TC-REW-021", "CAM-01", 32, 24)
    print(f"Test Discrepancy: Disc={disc_pct}%, Diff={diff}, Severity={sev}")
    print("Reason:", reason)
