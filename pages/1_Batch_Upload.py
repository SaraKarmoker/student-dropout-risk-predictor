from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

import style

st.set_page_config(page_title="Batch Risk List", page_icon="📋", layout="centered")
style.apply()
style.sidebar_about()


@st.cache_resource
def load_model():
    return joblib.load(Path(__file__).parent.parent / "dropout_model.joblib")


bundle = load_model()
model = bundle["model"]
features = bundle["features"]
high_cut = bundle["high_cut"]
medium_cut = bundle["medium_cut"]


def level(p):
    if p >= high_cut:
        return "High"
    if p >= medium_cut:
        return "Medium"
    return "Low"


def color_level(value):
    colors = {"High": "#D64545", "Medium": "#E8A317", "Low": "#2E9E6B"}
    return f"background-color: {colors[value]}; color: white; font-weight: 600"


style.hero(
    "Batch Risk List",
    "Upload a CSV with one row per student. Every student is ranked from highest to "
    "lowest dropout risk, using their first 60 days of data.",
)

sample = pd.DataFrame({
    "student_id": ["S001", "S002", "S003"],
    "total_clicks": [600, 25, 300],
    "active_days": [25, 3, 15],
    "clicks_first30": [300, 20, 200],
    "clicks_next30": [300, 5, 100],
    "assessments_done": [2, 0, 1],
    "assessments_missed": [0, 2, 1],
    "avg_score": [70, 0, 45],
    "avg_delay": [0, 0, 3],
    "num_of_prev_attempts": [0, 0, 1],
    "studied_credits": [60, 60, 60],
})

with st.container(key="card_upload"):
    st.markdown("#### 📂 Upload your file")
    st.download_button("Download a sample CSV to see the format",
                       sample.to_csv(index=False), "sample_students.csv", "text/csv")
    st.caption("Required columns: " + ", ".join(features) +
               ". An optional student_id column is kept in the results.")
    uploaded = st.file_uploader("Upload your CSV", type="csv")

if uploaded is not None:
    data = pd.read_csv(uploaded)

    missing = [c for c in features if c not in data.columns]
    if missing:
        st.error("Your file is missing these columns: " + ", ".join(missing))
        st.stop()

    X = data[features].apply(pd.to_numeric, errors="coerce")
    bad = X.isna().any(axis=1)
    if bad.any():
        st.warning(f"{int(bad.sum())} row(s) had missing or non-numeric values and were skipped.")
    data = data[~bad].copy()
    X = X[~bad]

    if data.empty:
        st.error("No valid rows to score.")
        st.stop()

    data["risk_score"] = model.predict_proba(X.astype(float))[:, 1].round(3)
    data["risk_level"] = data["risk_score"].apply(level)
    data = data.sort_values("risk_score", ascending=False).reset_index(drop=True)
    data.insert(0, "rank", data.index + 1)

    st.markdown(f"### Results for {len(data)} students")
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 High risk", int((data["risk_level"] == "High").sum()))
    c2.metric("🟠 Medium risk", int((data["risk_level"] == "Medium").sum()))
    c3.metric("🟢 Low risk", int((data["risk_level"] == "Low").sum()))

    styler = data.style
    apply_map = getattr(styler, "map", None) or styler.applymap
    styled = apply_map(color_level, subset=["risk_level"]).format({"risk_score": "{:.3f}"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.download_button("Download the ranked list as CSV",
                       data.to_csv(index=False),
                       "ranked_risk_list.csv", "text/csv")
    st.caption(
        "Risk levels use cutoffs learned from the model's test data, so a small upload "
        "may have no High-risk students at all. The risk score is a model score, "
        "not a certain prediction."
    )

st.divider()
style.model_card()
style.footer()
