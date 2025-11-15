import streamlit as st

# ----------------- Page config -----------------
st.set_page_config(
    page_title="Calculator — Classic",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------- CSS (hide streamlit chrome + perfect centering) -----------------
st.markdown(
    """
    <style>
    /* Remove Streamlit header, menu, and footer (the unwanted rectangle) */
    # MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden; height: 0; margin: 0; padding: 0;}

    /* Page background and reset */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #000000;   /* black background for app */
        color: #ffffff;
        height: 100%;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* Remove default top padding of Streamlit's main block container */
    .css-18e3th9, .block-container {  /* common block container classes */
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0 !important;
    }

    /* True full-viewport centering */
    .calc-center {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh !important; /* full viewport height */
        width: 100%;
        padding: 0;
        margin: 0;
    }

    /* White card (calculator) */
    .calc-card {
        background: #ffffff;      /* white calculator area */
        color: #000000;
        width: 420px;
        max-width: 92vw;
        padding: 28px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .calc-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
        text-align: center;
    }

    /* Make text inputs look larger and consistent */
    input[type="text"] {
        height: 44px !important;
        border-radius: 8px !important;
        padding-left: 12px !important;
        font-size: 16px !important;
        border: 1px solid #dcdcdc !important;
    }

    /* Make select (dropdown) look white */
    select {
        background-color: #ffffff !important;
        color: #000000 !important;
        height: 44px !important;
        border-radius: 8px !important;
        padding-left: 8px !important;
        font-size: 16px !important;
        border: 1px solid #dcdcdc !important;
    }

    /* Style the Calculate button (blue background, white text) */

    div.stButton > button {
        background-color: #007BFF !important;   /* Blue */
        color: #ffffff !important;              /* White text */
        border: 1px solid #0056b3 !important;   /* Darker blue border */
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-weight: 600 !important;
        height: 44px !important;
        width: 100% !important;
        box-shadow: none !important;
    }

    .result-box {
        background: #f7f7f7;
        color: #000;
        padding: 10px 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-weight: 600;
    }

    .muted {
        color: #666666;
        font-size: 13px;
        margin-top: 6px;
    }

    /* Ensure there is no mysterious rectangle above the card by forcing container spacing to zero */
    .stApp, .main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- Layout (no stray spacers that create rectangles) -----------------
# Create a single container which will be centered by the CSS above
#st.markdown('<div class="calc-center">', unsafe_allow_html=True)
#st.markdown('<div class="calc-card">', unsafe_allow_html=True)

# Title and helper text (inside card only)
st.markdown('<div class="calc-title">🧮 Simple Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="muted">Enter numbers in the text fields below. Operators in dropdown (white).</div>', unsafe_allow_html=True)

# Inputs: two text fields (numbers) — placed side-by-side
col1, col2 = st.columns([1, 1])
with col1:
    a_str = st.text_input("First number", value="", key="a_input", placeholder="e.g. 12.5")
with col2:
    b_str = st.text_input("Second number", value="", key="b_input", placeholder="e.g. 3")

# Operator dropdown (white by CSS)
operators = ["+", "-", "×", "÷", "^ (power)", "% (modulus)"]
op = st.selectbox("Operator", operators, index=0, help="Choose operator from the white dropdown")

# Calculate button (styled to appear like a text field)
calc_clicked = st.button("Calculate")

# Helper to parse numeric input (supports ints and floats)
def parse_number(s):
    s = s.strip()
    if s == "":
        return None, "empty"
    # allow comma as thousands separators (common) - remove them
    s = s.replace(",", "")
    try:
        # prefer integer when possible
        if "." in s:
            return float(s), None
        else:
            return int(s), None
    except Exception:
        # attempt float conversion fallback
        try:
            return float(s), None
        except Exception:
            return None, f"invalid number: {s}"

# Perform calculation and show result
result = None
error = None
if calc_clicked:
    a, a_err = parse_number(a_str)
    b, b_err = parse_number(b_str)

    if a_err:
        error = f"First number error: {a_err}"
    elif b_err:
        error = f"Second number error: {b_err}"
    else:
        try:
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op == "×":
                result = a * b
            elif op == "÷":
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                result = a / b
            elif op == "^ (power)":
                result = a ** b
            elif op == "% (modulus)":
                result = a % b
            else:
                error = "Unknown operator"
        except ZeroDivisionError:
            error = "Error: division by zero"
        except Exception as e:
            error = f"Computation error: {e}"

# Show result or error (inside card)
if result is not None:
    st.markdown(f'<div class="result-box" style="margin-top:12px">Result: {result}</div>', unsafe_allow_html=True)
elif error:
    st.error(error)

# Close card and center div
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
