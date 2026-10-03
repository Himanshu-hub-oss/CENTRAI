import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Import Outfit / Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Top Header Styling */
        .header-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.2rem;
        }
        .header-subtitle {
            font-size: 1.0rem;
            color: #f8fafc;
            margin-bottom: 1.5rem;
        }

        /* Metric Cards */
        .metric-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 18px 22px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 4px;
        }
        .metric-footer {
            font-size: 0.78rem;
            color: #94a3b8;
            margin-top: 4px;
        }

        /* Badges */
        .badge-high {
            background-color: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .badge-medium {
            background-color: #fffbeb;
            color: #d97706;
            border: 1px solid #fde68a;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .badge-low {
            background-color: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .flag-label {
            display: inline-block;
            background-color: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, footer="", color="#0f172a"):
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-footer">{footer}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
