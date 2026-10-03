import os
import cv2
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class InspectionReportGenerator:
    def __init__(self, output_dir='reports'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, centre_data, compliance_items, alerts_list, evidence_img_path=None, officer_notes="Inspection completed via AI Monitoring Suite."):
        """
        Generates a formal Government PDF Inspection Report for a Training Centre.
        Returns path to generated PDF.
        """
        centre_id = centre_data.get('centre_id', 'TC-000')
        filename = f"Inspection_Report_{centre_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography & Color Palette
        primary_color = colors.HexColor("#0f172a") # Navy Dark
        secondary_color = colors.HexColor("#0284c7") # Ocean Blue
        danger_color = colors.HexColor("#dc2626") # Red
        success_color = colors.HexColor("#16a34a") # Green
        card_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=primary_color,
            alignment=1 # Centered
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            alignment=1
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=secondary_color,
            spaceBefore=10,
            spaceAfter=6
        )

        normal_style = ParagraphStyle('NormalText', parent=styles['Normal'], fontSize=9, leading=12)
        bold_style = ParagraphStyle('BoldText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12)

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("MINISTRY OF SKILL DEVELOPMENT & ENTREPRENEURSHIP", subtitle_style))
        elements.append(Paragraph("SkillCentre Guardian AI — Inspection Report", title_style))
        elements.append(Paragraph(f"Official Audit Document | Generated: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=secondary_color, spaceBefore=5, spaceAfter=15))

        # 2. Centre Overview Table Card
        risk_lvl = centre_data.get('risk_level', 'LOW RISK')
        risk_clr = danger_color if risk_lvl == 'HIGH RISK' else (colors.HexColor("#d97706") if risk_lvl == 'MEDIUM RISK' else success_color)

        summary_data = [
            [
                Paragraph("<b>Centre ID:</b>", bold_style), Paragraph(str(centre_data.get('centre_id')), normal_style),
                Paragraph("<b>State / District:</b>", bold_style), Paragraph(f"{centre_data.get('state')} / {centre_data.get('district')}", normal_style)
            ],
            [
                Paragraph("<b>Centre Name:</b>", bold_style), Paragraph(str(centre_data.get('centre_name')), normal_style),
                Paragraph("<b>Course Name:</b>", bold_style), Paragraph(str(centre_data.get('course')), normal_style)
            ],
            [
                Paragraph("<b>Registered Trainees:</b>", bold_style), Paragraph(str(centre_data.get('registered_trainees')), normal_style),
                Paragraph("<b>Current Occupancy:</b>", bold_style), Paragraph(f"{centre_data.get('present_trainees')} ({centre_data.get('attendance_pct')}%)", normal_style)
            ],
            [
                Paragraph("<b>Compliance Score:</b>", bold_style), Paragraph(f"{centre_data.get('infra_compliance_pct')}%", normal_style),
                Paragraph("<b>Risk Status:</b>", bold_style), Paragraph(f"<font color='{risk_clr.hexval()}'><b>{risk_lvl} (Score: {centre_data.get('risk_score')})</b></font>", normal_style)
            ]
        ]

        t_summary = Table(summary_data, colWidths=[1.3*inch, 2.3*inch, 1.4*inch, 2.3*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), card_bg),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 15))

        # 3. AI Alerts & Anomaly Summary
        elements.append(Paragraph("1. AI Alerts & Anomaly Audit", section_heading))
        if alerts_list:
            alert_table_data = [[
                Paragraph("<b>Alert ID</b>", bold_style),
                Paragraph("<b>Type</b>", bold_style),
                Paragraph("<b>Severity</b>", bold_style),
                Paragraph("<b>AI Confidence</b>", bold_style),
                Paragraph("<b>Reason / Details</b>", bold_style)
            ]]
            for a in alerts_list:
                alert_table_data.append([
                    Paragraph(str(a.get('alert_id')), normal_style),
                    Paragraph(str(a.get('alert_type')), normal_style),
                    Paragraph(f"<font color='red'><b>{a.get('severity')}</b></font>" if a.get('severity')=='CRITICAL' else str(a.get('severity')), normal_style),
                    Paragraph(f"{a.get('ai_confidence')}%", normal_style),
                    Paragraph(str(a.get('reason')), normal_style)
                ])
            t_alerts = Table(alert_table_data, colWidths=[1.0*inch, 1.5*inch, 1.0*inch, 1.1*inch, 2.7*inch])
            t_alerts.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(t_alerts)
        else:
            elements.append(Paragraph("No active compliance alerts or attendance anomalies detected for this centre.", normal_style))
        elements.append(Spacer(1, 15))

        # 4. Infrastructure & Compliance Breakdown (AI Detected vs Officer Verified)
        elements.append(Paragraph("2. Infrastructure Compliance Checklist", section_heading))
        if compliance_items:
            comp_table_data = [[
                Paragraph("<b>Item Name</b>", bold_style),
                Paragraph("<b>Category</b>", bold_style),
                Paragraph("<b>Verification Mode</b>", bold_style),
                Paragraph("<b>Status</b>", bold_style),
                Paragraph("<b>Remarks</b>", bold_style)
            ]]
            for item in compliance_items:
                v_mode = item.get('ai_detected_status') if item.get('ai_detected_status') else "Officer Verified"
                comp_table_data.append([
                    Paragraph(str(item.get('item_name')), normal_style),
                    Paragraph(str(item.get('category')), normal_style),
                    Paragraph(f"<b>{v_mode}</b>", normal_style),
                    Paragraph(str(item.get('officer_verified_status')), normal_style),
                    Paragraph(str(item.get('remarks')), normal_style)
                ])
            t_comp = Table(comp_table_data, colWidths=[1.8*inch, 1.1*inch, 1.4*inch, 1.2*inch, 1.8*inch])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(t_comp)
        elements.append(Spacer(1, 15))

        # 5. Visual Evidence Frame (if provided)
        if evidence_img_path and os.path.exists(evidence_img_path):
            elements.append(Paragraph("3. Visual Evidence Snapshot", section_heading))
            try:
                img_flowable = RLImage(evidence_img_path, width=5.5*inch, height=3.0*inch)
                elements.append(img_flowable)
                elements.append(Paragraph("<i>Snapshot captured by AI Monitoring Engine during live occupancy assessment.</i>", subtitle_style))
                elements.append(Spacer(1, 15))
            except Exception as e:
                print(f"[PDFGenerator] Image embedding error: {e}")

        # 6. Officer Remarks & Verification Sign-off
        elements.append(Paragraph("4. Inspecting Officer Verification", section_heading))
        elements.append(Paragraph(f"<b>Officer Remarks:</b> {officer_notes}", normal_style))
        elements.append(Spacer(1, 25))

        sig_table_data = [
            [Paragraph("<b>Inspecting Officer Name:</b> ___________________", normal_style), Paragraph("<b>Signature & Seal:</b> ___________________", normal_style)],
            [Paragraph("<b>Designation:</b> District Nodal Officer", normal_style), Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}", normal_style)]
        ]
        t_sig = Table(sig_table_data, colWidths=[3.6*inch, 3.6*inch])
        t_sig.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 8)]))
        elements.append(t_sig)

        doc.build(elements)
        print(f"[PDFGenerator] PDF report generated successfully at: {pdf_path}")
        return pdf_path

if __name__ == "__main__":
    gen = InspectionReportGenerator()
    dummy_c = {
        'centre_id': 'TC-REW-021',
        'centre_name': 'PMKVY Hub Rewa',
        'state': 'Madhya Pradesh',
        'district': 'Rewa',
        'course': 'Solar PV Technician',
        'registered_trainees': 35,
        'present_trainees': 18,
        'attendance_pct': 51.4,
        'infra_compliance_pct': 68.0,
        'risk_score': 74.5,
        'risk_level': 'HIGH RISK'
    }
    dummy_a = [{'alert_id': 'AL-REW-101', 'alert_type': 'Attendance Anomaly', 'severity': 'CRITICAL', 'ai_confidence': 95.4, 'reason': 'Attendance dropped to 51.4%'}]
    gen.generate_pdf(dummy_c, [], dummy_a)
