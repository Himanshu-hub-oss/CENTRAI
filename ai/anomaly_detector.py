import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

MODEL_SAVE_PATH = 'ai/models/isolation_forest_attendance.joblib'
DATASET_PATH = r'f:\SIH 26245\2018-2019_Daily_Attendance_20240429.csv\2018-2019_Daily_Attendance_20240429.csv'

class AttendanceAnomalyDetector:
    def __init__(self):
        """
        Attendance Anomaly Detection Engine using Scikit-Learn IsolationForest.
        Trained on real historical 2018-2019 daily attendance records (277k rows).
        """
        self.model = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(MODEL_SAVE_PATH):
            print(f"[AnomalyDetector] Loading pre-trained Isolation Forest model from {MODEL_SAVE_PATH}")
            try:
                self.model = joblib.load(MODEL_SAVE_PATH)
                return
            except Exception as e:
                print(f"[AnomalyDetector] Error loading saved model: {e}")

        print("[AnomalyDetector] Training Isolation Forest model on daily attendance dataset...")
        if os.path.exists(DATASET_PATH):
            df = pd.read_csv(DATASET_PATH)
            df['Attendance_Pct'] = (df['Present'] / df['Enrolled']) * 100
            df['Absent_Pct'] = (df['Absent'] / df['Enrolled']) * 100
            
            # Feature matrix: Attendance %, Absent %, Enrolled Count
            X = df[['Attendance_Pct', 'Absent_Pct', 'Enrolled']].dropna()
            
            # Isolation Forest with 5% contamination target for extreme drops
            iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            iso.fit(X)
            self.model = iso
            
            os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_SAVE_PATH)
            print(f"[AnomalyDetector] Model successfully trained and saved to {MODEL_SAVE_PATH}")
        else:
            print(f"[AnomalyDetector] Dataset not found at {DATASET_PATH}. Using fallback synthetic model fit.")
            X_dummy = np.random.normal(85, 10, (1000, 3))
            iso = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
            iso.fit(X_dummy)
            self.model = iso

    def detect_anomaly(self, current_attendance_pct, enrolled_count, historical_7d_avg=85.0):
        """
        Analyzes current attendance and checks for statistical and anomaly score deviations.
        Returns:
            is_anomaly (bool): True if unusual attendance pattern detected
            anomaly_score (float): Calculated anomaly score (0.0 to 1.0)
            reason (str): Human-interpretable clear explanation for decision support
        """
        absent_pct = max(0.0, 100.0 - current_attendance_pct)
        features = pd.DataFrame([[current_attendance_pct, absent_pct, enrolled_count]], 
                                columns=['Attendance_Pct', 'Absent_Pct', 'Enrolled'])

        # Predict anomaly using Isolation Forest (-1: Anomaly, 1: Normal)
        pred = self.model.predict(features)[0]
        decision_score = self.model.decision_function(features)[0] # Lower score = higher anomaly

        # Normalize decision score to 0.0 - 1.0 scale (higher = more anomalous)
        normalized_score = round(float(np.clip(0.5 - decision_score * 2, 0.0, 1.0)), 2)

        # Rule-based hybrid boost for massive drops (e.g. historical drop > 25%)
        drop_pct = historical_7d_avg - current_attendance_pct
        is_anomaly = (pred == -1) or (current_attendance_pct < 50.0) or (drop_pct >= 25.0)

        # Build transparent explanation text
        reasons = []
        if current_attendance_pct < 50.0:
            reasons.append(f"Critical attendance drop ({current_attendance_pct:.1f}% vs 50% threshold)")
        if drop_pct >= 25.0:
            reasons.append(f"Significant 7-day deviation: Dropped by {drop_pct:.1f}% (Previous 7-Day Avg: {historical_7d_avg:.1f}%, Current: {current_attendance_pct:.1f}%)")
        if pred == -1 and not reasons:
            reasons.append(f"Isolation Forest flags pattern as statistical outlier (Anomaly score: {normalized_score})")

        if not reasons:
            reason_str = f"Attendance is within normal baseline range ({current_attendance_pct:.1f}%)."
        else:
            reason_str = " | ".join(reasons)

        return is_anomaly, normalized_score, reason_str

if __name__ == "__main__":
    detector = AttendanceAnomalyDetector()
    # Test normal
    anom1, score1, reason1 = detector.detect_anomaly(current_attendance_pct=88.0, enrolled_count=30, historical_7d_avg=90.0)
    print("Normal Case Test:", anom1, score1, reason1)
    
    # Test drop anomaly
    anom2, score2, reason2 = detector.detect_anomaly(current_attendance_pct=42.0, enrolled_count=30, historical_7d_avg=88.0)
    print("Anomaly Case Test:", anom2, score2, reason2)
