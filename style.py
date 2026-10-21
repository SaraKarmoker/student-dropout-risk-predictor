import streamlit as st

# Numbers measured on test students the model never saw (from the Colab notebook)
MODEL_AUC = 0.712
TEST_STUDENTS = 7909
RATE_HIGH, RATE_MEDIUM, RATE_LOW, RATE_ALL = 36.9, 22.7, 9.6, 14.9

LEVELS = {
    "High": {
        "color": "#D64545",
        "title": "HIGH RISK",
        "action": "Prioritise this student for outreach. Suggested: a personal check-in "
                  "by a mentor, a review of missed assessments, and an offer of tutoring "
                  "or study support.",
    },
    "Medium": {
        "color": "#E8A317",
        "title": "MEDIUM RISK",
        "action": "Keep an eye on this student. Suggested: a friendly reminder about "
                  "upcoming deadlines and information about the support available.",
    },
    "Low": {
        "color": "#2E9E6B",
        "title": "LOW RISK",
        "action": "No special action needed. Continue normal monitoring.",
    },
}

CSS = """
<style>
.stApp { background: #F4F7FB; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 960px; }
#MainMenu, footer { visibility: hidden; }
h3, h4 { color: #0B2E4F; font-weight: 700; }
.hero { background: linear-gradient(135deg, #0B2E4F 0%, #0B5CAD 100%); border-radius: 16px; padding: 2rem 2rem 1.7rem 2rem; margin-bottom: 1.4rem; box-shadow: 0 6px 18px rgba(11,46,79,0.18); }
.hero-badge { display: inline-block; background: rgba(255,255,255,0.16); color: #FFFFFF; font-size: 0.72rem; letter-spacing: 0.12em; font-weight: 600; padding: 0.25rem 0.7rem; border-radius: 999px; margin-bottom: 0.8rem; }
.hero-title { color: #FFFFFF; font-size: 2.1rem; font-weight: 800; line-height: 1.15; margin-bottom: 0.5rem; }
.hero-sub { color: #D5E4F5; font-size: 1rem; line-height: 1.5; max-width: 640px; }
div[class*="st-key-card"] { background: #FFFFFF; border: 1px solid #DCE5F0; border-radius: 14px; padding: 1.1rem 1.3rem 0.6rem 1.3rem; margin-bottom: 0.9rem; box-shadow: 0 2px 8px rgba(11,46,79,0.06); }
.result { background: #FFFFFF; border-radius: 14px; padding: 1.4rem 1.6rem; margin: 1.2rem 0 0.8rem 0; box-shadow: 0 4px 14px rgba(11,46,79,0.10); }
.result-label { color: #5B6B80; font-size: 0.72rem; letter-spacing: 0.12em; font-weight: 600; }
.result-level { font-size: 2.1rem; font-weight: 800; line-height: 1.2; margin: 0.2rem 0 0.3rem 0; }
.result-score { color: #14233A; font-size: 1rem; margin-bottom: 0.6rem; }
.gauge { position: relative; display: flex; height: 14px; margin: 1.1rem 0 0.4rem 0; }
.gauge div:first-child { border-radius: 7px 0 0 7px; }
.gauge div:nth-child(3) { border-radius: 0 7px 7px 0; }
.marker { position: absolute; top: -6px; width: 4px; height: 26px; background: #0B2E4F; border-radius: 2px; transform: translateX(-50%); }
.gauge-labels { display: flex; font-size: 0.75rem; color: #5B6B80; }
.gauge-labels span { text-align: center; white-space: nowrap; }
.action { background: #F4F7FB; border-radius: 10px; padding: 0.8rem 1rem; margin-top: 1rem; color: #14233A; font-size: 0.95rem; }
.chip { display: inline-block; background: #FDECEC; color: #A32B2B; border-radius: 999px; padding: 0.25rem 0.75rem; margin: 0.2rem 0.4rem 0.2rem 0; font-size: 0.85rem; font-weight: 500; }
.note { color: #5B6B80; font-size: 0.82rem; line-height: 1.5; }
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #DCE5F0; border-radius: 12px; padding: 0.8rem 1rem; }
div[data-testid="stFormSubmitButton"] button { background: #0B5CAD; color: #FFFFFF; border: none; border-radius: 10px; font-weight: 600; padding: 0.6rem 1.2rem; }
div[data-testid="stFormSubmitButton"] button:hover { background: #084A8C; color: #FFFFFF; }
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="hero-badge">EARLY-WARNING TOOL</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def sidebar_about():
    with st.sidebar:
        st.markdown("### About this tool")
        st.write("Estimates a student's risk of dropping out from their first 60 days "
                 "of activity, so support can reach the right students early.")
        st.caption("Model: Random Forest with 10 inputs\n\n"
                   "Data: Open University Learning Analytics Dataset (UK)")


def risk_card(level, prob, medium_cut, high_cut):
    info = LEVELS[level]
    m = medium_cut * 100
    h = (high_cut - medium_cut) * 100
    r = 100 - m - h
    pos = min(max(prob * 100, 0.5), 99.5)
    st.markdown(
        f'<div class="result" style="border-left: 8px solid {info["color"]};">'
        f'<div class="result-label">ESTIMATED RISK LEVEL</div>'
        f'<div class="result-level" style="color: {info["color"]};">{info["title"]}</div>'
        f'<div class="result-score">Model risk score: <b>{prob:.0%}</b></div>'
        f'<div class="gauge">'
        f'<div style="width: {m}%; background: #2E9E6B;"></div>'
        f'<div style="width: {h}%; background: #E8A317;"></div>'
        f'<div style="width: {r}%; background: #D64545;"></div>'
        f'<span class="marker" style="left: {pos}%;"></span></div>'
        f'<div class="gauge-labels"><span style="width: {m}%;">Low</span>'
        f'<span style="width: {h}%;">Medium</span><span style="width: {r}%;">High</span></div>'
        f'<div class="action"><b>What to do:</b> {info["action"]}</div></div>',
        unsafe_allow_html=True,
    )


def chips(items):
    html = "".join(f'<span class="chip">{item}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)


def model_card():
    st.markdown("### How reliable is this tool?")
    st.write(f"The model was tested on {TEST_STUDENTS:,} students it had never seen. "
             "This is what really happened to the students in each risk group:")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High risk", f"{RATE_HIGH}%", help="Share of High-risk students who really dropped out")
    c2.metric("Medium risk", f"{RATE_MEDIUM}%", help="Share of Medium-risk students who really dropped out")
    c3.metric("Low risk", f"{RATE_LOW}%", help="Share of Low-risk students who really dropped out")
    c4.metric("All students", f"{RATE_ALL}%", help="Overall dropout rate in the test group")
    st.markdown(
        f'<div class="note">Ranking quality (AUC): <b>{MODEL_AUC}</b> (0.5 is random guessing, '
        f'1.0 is perfect). A High-risk label does not mean the student will drop out: about '
        f'6 in 10 High-risk students stayed. Use the result to decide who to support first.</div>',
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        '<div class="note" style="margin-top: 1.5rem; text-align: center;">'
        'Academic project. Trained on Open University (UK) data and not validated on other '
        'institutions. It gives a risk estimate, not a certain prediction, and should support '
        "a counselor's judgement, not replace it.</div>",
        unsafe_allow_html=True,
    )
