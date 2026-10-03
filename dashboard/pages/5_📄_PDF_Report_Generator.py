import os
import sys
import sqlite3
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import get_db_connection
from backend.report_generator import InspectionReportGenerator

st.set_page_config(page_title="PDF Report Generator | Guardian AI", layout="wide")

st.title(" Module 11: Official PDF Inspection Report Generator")
st.markdown("Generate and Download Formal Government Audit Reports in One Click.")

conn = get_db_connection()
centres_df = pd.read_sql_query("SELECT * FROM training_centres", conn)

selected_c_str = st.selectbox("Select Training Centre for Report Generation", [f"{row['centre_id']} - {row['centre_name']}" for _, row in centres_df.iterrows()])
cid = selected_c_str.split(" - ")[0]

centre_row = centres_df[centres_df['centre_id'] == cid].iloc[0].to_dict()
comp_items = pd.read_sql_query("SELECT * FROM compliance_items WHERE centre_id = ?", conn, params=(cid,)).to_dict('records')
alerts_items = pd.read_sql_query("SELECT * FROM alerts WHERE centre_id = ?", conn, params=(cid,)).to_dict('records')
conn.close()

officer_remarks = st.text_area("Inspecting Officer Field Remarks", "Centre inspection completed. AI occupancy estimates verified against physical attendance register.")

if st.button(" Generate PDF Inspection Report", type="primary"):
    generator = InspectionReportGenerator()
    pdf_path = generator.generate_pdf(
        centre_data=centre_row,
        compliance_items=comp_items,
        alerts_list=alerts_items,
        officer_notes=officer_remarks
    )
    
    with open(pdf_path, "rb") as f:
        st.download_button(" Download Official PDF Report", f, file_name=os.path.basename(pdf_path), mime="application/pdf")
    st.success(f"Report generated successfully: `{os.path.basename(pdf_path)}`")
