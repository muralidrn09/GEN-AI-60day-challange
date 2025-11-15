import streamlit as st

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="BMI — Mobile",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------- Styles: Dark + iPhone-ish + Neon Buttons -----------------
STYLE = """
<style>
/* Page background (dark gradient) */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0f1724 0%, #071021 100%);
    color: #e6eef8;
    min-height: 100vh;
}

/* Center content and limit width to mobile size */
.main > div {
    max-width: 390px;     /* typical mobile width */
    margin: 28px auto;
    padding: 0 14px;
}

/* iPhone style top notch / header container */
.app-header {
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 12px;
}
.app-header .dot {
    width: 8px;
    height: 8px;
    background: linear-gradient(90deg,#34d399,#06b6d4);
    border-radius: 50%;
    box-shadow: 0 6px 22px rgba(3, 218, 197, 0.12);
}

/* Mobile card (glassmorphic-ish, but dark for iPhone look) */
.mobile-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 28px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(2,6,23,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
}

/* Title styling */
h1 {
    font-size: 20px;
    margin: 4px 0 8px 0;
    text-align: center;
}

/* Input styles (number inputs) */
input[type="number"], .stNumberInput>div>input {
    background: rgba(255,255,255,0.03) !important;
    color: #000000 !important;
    border-radius: 12px !important;
    padding: 10px 12px !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
}

/* Slider track/text color */
div[data-baseweb="slider"] { color: #e6eef8; }

/* Neon / modern button */
div.stButton > button, button[data-testid="stButton"] {
    width: 100%;
    border-radius: 14px;
    padding: 12px 14px;
    font-weight: 800;
    letter-spacing: 0.3px;
    border: none;
    cursor: pointer;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    color: white;
    box-shadow:
        0 6px 18px rgba(12,0,80,0.45),
        0 0 24px rgba(124,58,237,0.18),
        0 0 40px rgba(6,182,212,0.12);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}

/* Hover and active glow */
div.stButton > button:hover, button[data-testid="stButton"]:hover {
    transform: translateY(-3px);
    box-shadow:
        0 10px 28px rgba(12,0,80,0.55),
        0 0 48px rgba(124,58,237,0.28),
        0 0 72px rgba(6,182,212,0.20);
}

/* Result badge */
.result {
    margin-top: 12px;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    font-weight: 700;
}

/* Classification chips */
.chip {
    display:inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    font-weight:700;
    margin-top:8px;
}

/* Small footer text */
.footer {
    font-size: 12px;
    color: #a9becf;
    text-align: center;
    margin-top: 10px;
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)

# ----------------- Header / iPhone notch feel -----------------
st.markdown('<div class="app-header"><div class="dot"></div><div style="width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.06)"></div></div>', unsafe_allow_html=True)

# ----------------- UI Card -----------------
#st.markdown('<div class="mobile-card">', unsafe_allow_html=True)

st.markdown("<h1>📱 BMI Calculator</h1>", unsafe_allow_html=True)
st.markdown("Enter your details and tap **Calculate**", unsafe_allow_html=True)

# Inputs (sliders & number inputs for better mobile UX)
col1, col2 = st.columns([1, 1])

with col1:
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, step=1, format="%d")
with col2:
    weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70, step=1, format="%d")

age = st.slider("Age (yrs)", min_value=5, max_value=100, value=30)

# Option to toggle units (iPhone style toggle by selectbox)
unit = st.selectbox("Units", ["Metric (cm / kg)"], index=0)

# Calculate button (neon)
calculate = st.button("Calculate BMI")

# Logic & output
if calculate:
    if height <= 0:
        st.error("Please enter a valid height.")
    else:
        bmi = weight / ((height / 100) ** 2)
        bmi_text = f"{bmi:.2f}"
        # classification
        if bmi < 18.5:
            cls = "Underweight"
            color_bg = "linear-gradient(90deg,#0ea5e9,#7dd3fc)"
            chip_color = "#0ea5e9"
        elif 18.5 <= bmi < 24.9:
            cls = "Normal"
            color_bg = "linear-gradient(90deg,#10b981,#34d399)"
            chip_color = "#10b981"
        elif 25 <= bmi < 29.9:
            cls = "Overweight"
            color_bg = "linear-gradient(90deg,#f59e0b,#f97316)"
            chip_color = "#f59e0b"
        else:
            cls = "Obesity"
            color_bg = "linear-gradient(90deg,#ef4444,#f43f5e)"
            chip_color = "#ef4444"

        st.markdown(
            f"""
            <div class="result" style="background: rgba(255,255,255,0.02);">
                <div style="font-size:28px;">BMI: <strong>{bmi_text}</strong></div>
                <div style="margin-top:8px;">
                    <span class="chip" style="background:{color_bg}; color:white;">{cls}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # helpful message
        st.markdown(f'<div class="footer">Aged {age} — BMI is a general indicator; consult a health professional for personalised advice.</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Bottom spacing
st.write("")
