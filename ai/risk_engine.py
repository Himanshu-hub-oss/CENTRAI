class CentreRiskEngine:
    def __init__(self, weights=None):
        """
        Transparent Centre Risk Scoring Engine.
        Combines attendance anomaly, infrastructure compliance, engagement score, alert history, and inspection status.
        Configurable weights default to:
        - Attendance Anomaly: 30%
        - Infrastructure Compliance: 25%
        - Engagement Indicator: 20%
        - Historical Alerts: 15%
        - Inspection Delay: 10%
        """
        if weights is None:
            self.weights = {
                'attendance': 0.30,
                'infra': 0.25,
                'engagement': 0.20,
                'alerts': 0.15,
                'inspection': 0.10
            }
        else:
            self.weights = weights

    def calculate_risk(self, attendance_pct, infra_compliance_pct, engagement_score, open_alert_count, days_since_last_inspection):
        """
        Calculates a 0 - 100 Centre Risk Score with human-understandable breakdown.
        Returns:
            risk_score (float): 0.0 (Safest) to 100.0 (Highest Risk)
            risk_level (str): LOW RISK | MEDIUM RISK | HIGH RISK
            breakdown (dict): Breakdown of sub-scores
            reasons (list): Plain-text explainable bullet points
        """
        # Sub-score calculations (each mapped to 0-100 where 100 is WORST/highest risk)
        
        # 1. Attendance Sub-score: Drops below 80% start penalizing
        att_risk = max(0.0, min(100.0, (85.0 - attendance_pct) * 2.5))
        if attendance_pct < 50.0:
            att_risk = 100.0

        # 2. Infra Sub-score: Direct inverse of compliance rate
        infra_risk = max(0.0, min(100.0, 100.0 - infra_compliance_pct))

        # 3. Engagement Sub-score: Direct inverse of engagement score
        eng_risk = max(0.0, min(100.0, 100.0 - engagement_score))

        # 4. Alert History Sub-score: 20 points per open alert (max 100)
        alert_risk = min(100.0, open_alert_count * 20.0)

        # 5. Inspection Delay Sub-score: Over 30 days starts escalating
        inspection_risk = max(0.0, min(100.0, (days_since_last_inspection - 30.0) * 2.0))

        # Weighted composite sum
        risk_score = round(
            (att_risk * self.weights['attendance']) +
            (infra_risk * self.weights['infra']) +
            (eng_risk * self.weights['engagement']) +
            (alert_risk * self.weights['alerts']) +
            (inspection_risk * self.weights['inspection']),
            1
        )

        # Categorize
        if risk_score <= 35.0:
            risk_level = "LOW RISK"
        elif risk_score <= 65.0:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "HIGH RISK"

        # Generate transparent explainable reasons
        reasons = []
        if attendance_pct < 70.0:
            reasons.append(f"Low attendance rate ({attendance_pct:.1f}% vs 85% target)")
        if infra_compliance_pct < 80.0:
            reasons.append(f"Infrastructure compliance deficit ({infra_compliance_pct:.1f}% compliance rate)")
        if engagement_score < 60.0:
            reasons.append(f"Subdued classroom engagement indicator ({engagement_score:.1f} / 100)")
        if open_alert_count > 0:
            reasons.append(f"{open_alert_count} active open AI alerts require officer verification")
        if days_since_last_inspection > 45:
            reasons.append(f"Physical inspection overdue by {days_since_last_inspection} days")

        if not reasons:
            reasons.append("All operational parameters within safe government compliance limits.")

        breakdown = {
            "attendance_subscore": round(att_risk, 1),
            "infra_subscore": round(infra_risk, 1),
            "engagement_subscore": round(eng_risk, 1),
            "alert_subscore": round(alert_risk, 1),
            "inspection_subscore": round(inspection_risk, 1)
        }

        return risk_score, risk_level, breakdown, reasons

if __name__ == "__main__":
    engine = CentreRiskEngine()
    score, level, bdown, reasons = engine.calculate_risk(
        attendance_pct=48.0, 
        infra_compliance_pct=72.0, 
        engagement_score=55.0, 
        open_alert_count=3, 
        days_since_last_inspection=50
    )
    print(f"Risk Test: Level={level} (Score: {score})")
    print("Reasons:", reasons)
