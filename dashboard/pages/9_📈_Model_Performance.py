import os
import sys
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai.model_evaluator import ModelEvaluator


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Model Evaluation | CENTRAI",
    page_icon="📈",
    layout="wide"
)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def get_metric(results, *keys):
    """
    Safely retrieve a metric from evaluator results.

    Returns:
        Actual metric if available.
        None if metric is unavailable/not measured.
    """
    if not isinstance(results, dict):
        return None

    for key in keys:
        if key in results:
            value = results[key]

            # Ignore None / empty values
            if value is not None and value != "":
                return value

    return None


def format_metric(value, decimals=3):
    """
    Format metric safely.
    """
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def metric_label(value):
    """
    User-friendly label for unavailable metrics.
    """
    if value is None:
        return "N/A — Not Measured"

    return format_metric(value)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("📈 Model Evaluation & Accuracy Assessment")

st.markdown(
    """
    **Empirical Accuracy Evaluation**

    Model performance is displayed only when the corresponding metric
    is actually available from the evaluation pipeline.
    """
)


# ---------------------------------------------------------
# Run Evaluation
# ---------------------------------------------------------
try:

    evaluator = ModelEvaluator()

    with st.spinner("Running model evaluation..."):
        results = evaluator.evaluate_behaviour_dataset()

except Exception as e:

    st.error("Model evaluation could not be completed.")

    st.code(
        str(e),
        language="text"
    )

    st.info(
        "The evaluation page is protected from crashing, but the "
        "underlying evaluator needs to be checked."
    )

    st.stop()


# ---------------------------------------------------------
# Validate Results
# ---------------------------------------------------------
if not isinstance(results, dict):

    st.error(
        "Model evaluator returned an unexpected result format."
    )

    st.write("Returned type:", type(results).__name__)

    st.stop()


# ---------------------------------------------------------
# Debug / Evaluation Summary
# ---------------------------------------------------------
with st.expander("🔍 Evaluation Result Structure"):

    st.write("Available result keys:")

    st.code(
        "\n".join(str(key) for key in results.keys()),
        language="text"
    )


# ---------------------------------------------------------
# Extract Metrics
# ---------------------------------------------------------

# mAP@50
map50 = get_metric(
    results,
    "mAP50",
    "map50",
    "mAP@50",
    "map_50",
    "map_50_percent"
)

# Precision
mean_precision = get_metric(
    results,
    "mean_precision",
    "precision",
    "mean_precision_score"
)

# Recall
mean_recall = get_metric(
    results,
    "mean_recall",
    "recall",
    "mean_recall_score"
)

# F1
mean_f1 = get_metric(
    results,
    "mean_f1_score",
    "f1",
    "f1_score",
    "mean_f1"
)

# Class-wise metrics
class_metrics = get_metric(
    results,
    "class_metrics",
    "class_wise_metrics",
    "per_class_metrics"
)


# ---------------------------------------------------------
# Main Metrics
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "mAP@50",
        metric_label(map50)
    )

with c2:
    st.metric(
        "Mean Precision",
        metric_label(mean_precision)
    )

with c3:
    st.metric(
        "Mean Recall",
        metric_label(mean_recall)
    )

with c4:
    st.metric(
        "Mean F1-Score",
        metric_label(mean_f1)
    )


# ---------------------------------------------------------
# Metric Availability Notice
# ---------------------------------------------------------
missing_metrics = []

if map50 is None:
    missing_metrics.append("mAP@50")

if mean_precision is None:
    missing_metrics.append("Precision")

if mean_recall is None:
    missing_metrics.append("Recall")

if mean_f1 is None:
    missing_metrics.append("F1")


if missing_metrics:

    st.warning(
        "Some metrics are not available from the current evaluation "
        "pipeline: "
        + ", ".join(missing_metrics)
        + ". They are shown as N/A rather than using fabricated values."
    )


# ---------------------------------------------------------
# Class-wise Breakdown
# ---------------------------------------------------------
st.markdown("---")

st.subheader("🎯 Class-Wise Precision, Recall & F1 Breakdown")


if class_metrics is not None:

    try:

        if isinstance(class_metrics, dict):

            df_metrics = pd.DataFrame.from_dict(
                class_metrics,
                orient="index"
            )

        elif isinstance(class_metrics, list):

            df_metrics = pd.DataFrame(class_metrics)

        elif isinstance(class_metrics, pd.DataFrame):

            df_metrics = class_metrics.copy()

        else:

            df_metrics = pd.DataFrame()

        if not df_metrics.empty:

            st.dataframe(
                df_metrics,
                hide_index=True,
                use_container_width=True
            )

        else:

            st.info(
                "Class-wise evaluation data is currently unavailable."
            )

    except Exception as e:

        st.warning(
            "Class-wise metrics were returned but could not be "
            "displayed in table format."
        )

        with st.expander("Technical Details"):
            st.code(str(e))

else:

    st.info(
        "Class-wise metrics are not available from the current "
        "evaluation pipeline."
    )


# ---------------------------------------------------------
# Model Status & Capabilities
# ---------------------------------------------------------
st.markdown("---")

st.subheader("🤖 Model Status & Capabilities Registry")

st.caption(
    "Only documented/implemented capabilities are listed below. "
    "Metrics are not invented when unavailable."
)


status_data = [
    {
        "Module": "Person Detector",
        "Model Type": "YOLOv8 Base (Class 0)",
        "Status": "REAL MODEL",
        "Capability / Metric": "Person detection"
    },
    {
        "Module": "Behaviour Indicator",
        "Model Type": "YOLOv8 Custom",
        "Status": "REAL MODEL",
        "Capability / Metric": "Behaviour detection"
    },
    {
        "Module": "Attendance Anomaly",
        "Model Type": "Scikit-learn Isolation Forest",
        "Status": "REAL MODEL",
        "Capability / Metric": "Anomaly / risk detection"
    },
    {
        "Module": "Infrastructure Inventory",
        "Model Type": "YOLOv8 + Rule-Based Check",
        "Status": "REAL MODEL + RULE-BASED",
        "Capability / Metric": "Presence detection; officer verification required"
    },
    {
        "Module": "Equipment Operability",
        "Model Type": "Visual Analysis",
        "Status": "NOT TRAINED",
        "Capability / Metric": "Operability not verifiable from footage alone"
    }
]


status_df = pd.DataFrame(status_data)

st.dataframe(
    status_df,
    hide_index=True,
    use_container_width=True
)


# ---------------------------------------------------------
# Interpretation
# ---------------------------------------------------------
st.markdown("---")

st.subheader("📋 Evaluation Interpretation")

st.markdown(
    """
    **Metric definitions**

    - **mAP@50:** Mean Average Precision at IoU threshold 0.50.
    - **Precision:** Fraction of predicted positives that are correct.
    - **Recall:** Fraction of actual positives detected by the model.
    - **F1-Score:** Harmonic mean of precision and recall.

    **Important:** A metric is displayed only when it is returned by the
    actual evaluation pipeline. Missing metrics are shown as
    **N/A — Not Measured** rather than being estimated or fabricated.
    """
)


# ---------------------------------------------------------
# Evaluation Status
# ---------------------------------------------------------
st.markdown("---")

available_count = sum(
    value is not None
    for value in [
        map50,
        mean_precision,
        mean_recall,
        mean_f1
    ]
)

total_metrics = 4


if available_count == total_metrics:

    st.success(
        "All primary evaluation metrics are available from the "
        "current evaluation run."
    )

elif available_count > 0:

    st.info(
        f"{available_count}/{total_metrics} primary evaluation metrics "
        "are currently available."
    )

else:

    st.warning(
        "No primary evaluation metrics were returned by the current "
        "evaluation pipeline."
    )
