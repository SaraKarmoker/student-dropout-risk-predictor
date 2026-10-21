from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

import style

st.set_page_config(page_title="Student Dropout Risk Predictor", page_icon="🎓", layout="centered")
style.apply()
style.sidebar_about()


@st.cache_resource
def load_model():
    return joblib.load(Path(__file__).parent / "dropout_model.joblib")


bundle = load_model()
model = bundle["model"]
features = bundle["features"]
high_cut = bundle["high_cut"]
medium_cut = bundle["medium_cut"]

DEFAULTS = dict(c1=300, c2=300, days=25, done=2, missed=0, score=70,
                delay=0.0, prev=0, credits=60)
EXAMPLES = {
    "engaged": dict(c1=420, c2=380, days=34, done=3, missed=0, score=78,
                    delay=-1.0, prev=0, credits=60),
    "struggling": dict(c1=40, c2=8, days=5, done=0, missed=2, score=0,
                       delay=0.0, prev=1, credits=60),
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def load_example(name):
    for key, value in EXAMPLES[name].items():
        st.session_state[key] = value


style.hero(
    "Student Dropout Risk Predictor",
    "Enter what a student did in the first 60 days of their course to see their "
    "estimated dropout risk, so support can reach the right students early.",
)

st.write("**Quick demo:** load an example student, then press Predict.")
b1, b2, _ = st.columns([1, 1, 2])
b1.button("Example: engaged student", on_click=load_example, args=("engaged",), use_container_width=True)
b2.button("Example: struggling student", on_click=load_example, args=("struggling",), use_container_width=True)

with st.form("student_form"):
    with st.container(key="card_activity"):
        st.markdown("#### 🖥️ Online activity")
        col1, col2 = st.columns(2)
        clicks_first30 = col1.number_input(
            "Clicks in days 1-30", min_value=0, step=10, key="c1",
            help="Total clicks on the online learning platform in the first 30 days.")
        clicks_next30 = col2.number_input(
            "Clicks in days 31-60", min_value=0, step=10, key="c2",
            help="Total clicks on the online learning platform in days 31 to 60.")
        active_days = st.slider(
            "Days the student was active online (out of 60)", 0, 60, key="days",
            help="Number of different days with at least one click.")

    with st.container(key="card_assess"):
        st.markdown("#### 📝 Assessments (first 60 days)")
        col3, col4 = st.columns(2)
        assessments_done = col3.number_input(
            "Assessments submitted", min_value=0, step=1, key="done")
        assessments_missed = col4.number_input(
            "Assessments missed", min_value=0, step=1, key="missed",
            help="Assessments that were due but not submitted.")
        avg_score = st.slider(
            "Average score (0-100)", 0, 100, key="score",
            help="Ignored if no assessment has been submitted yet.")
        avg_delay = st.number_input(
            "Average submission delay (days)", step=1.0, key="delay",
            help="Days after the deadline. Negative means early, e.g. -3 = 3 days early.")

    with st.container(key="card_background"):
        st.markdown("#### 🎓 Course background")
        col5, col6 = st.columns(2)
        num_of_prev_attempts = col5.number_input(
            "Previous attempts at this course", min_value=0, step=1, key="prev")
        studied_credits = col6.number_input(
            "Credits studied this term", min_value=0, step=30, key="credits")

    submitted = st.form_submit_button("Predict dropout risk", use_container_width=True)

if submitted:
    score_used = avg_score if assessments_done > 0 else 0
    if assessments_done == 0 and avg_score > 0:
        st.info("No assessments were submitted, so the average score was treated as 0.")

    values = {
        "total_clicks": clicks_first30 + clicks_next30,
        "active_days": active_days,
        "clicks_first30": clicks_first30,
        "clicks_next30": clicks_next30,
        "assessments_done": assessments_done,
        "assessments_missed": assessments_missed,
        "avg_score": score_used,
        "avg_delay": avg_delay,
        "num_of_prev_attempts": num_of_prev_attempts,
        "studied_credits": studied_credits,
    }
    row = pd.DataFrame([values])[features].astype(float)
    prob = float(model.predict_proba(row)[0][1])

    if prob >= high_cut:
        level = "High"
    elif prob >= medium_cut:
        level = "Medium"
    else:
        level = "Low"

    style.risk_card(level, prob, medium_cut, high_cut)

    flags = []
    if assessments_missed >= 1:
        flags.append(f"Missed {assessments_missed} assessment(s)")
    if active_days < 15:
        flags.append("Active on fewer than 15 of the first 60 days")
    if clicks_next30 < clicks_first30 * 0.5:
        flags.append("Online activity dropped sharply in days 31-60")
    if score_used < 40 and assessments_done > 0:
        flags.append("Low average score")
    if flags:
        st.markdown("**Warning signs noticed in the inputs**")
        style.chips(flags)
        st.caption("These come from simple rules applied to your inputs. "
                   "They are separate from the model's score.")

st.divider()
style.model_card()
style.footer()
