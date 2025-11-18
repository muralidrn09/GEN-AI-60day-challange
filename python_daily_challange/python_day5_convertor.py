from typing import Tuple
import streamlit as st

# ---------- Conversion functions ----------
def inr_to_usd(inr: float, inr_per_usd: float) -> float:
    if inr_per_usd == 0:
        raise ValueError("Exchange rate must be non-zero")
    return inr / inr_per_usd

def usd_to_inr(usd: float, inr_per_usd: float) -> float:
    return usd * inr_per_usd

def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0

def f_to_c(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0

def cm_to_inch(cm: float) -> float:
    return cm / 2.54

def inch_to_cm(inch: float) -> float:
    return inch * 2.54

def kg_to_lb(kg: float) -> float:
    return kg * 2.2046226218487757

def lb_to_kg(lb: float) -> float:
    return lb / 2.2046226218487757

# Optional: function to format numbers nicely
def fmt(x: float, precision: int) -> str:
    return f"{x:,.{precision}f}"

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Unit Converter", layout="centered", page_icon="🔁")

st.title("🔁 Unit Converter")
st.write("Simple, accurate conversions for currency, temperature, length, and weight.")

# Sidebar controls
st.sidebar.header("Settings")
precision = st.sidebar.slider("Decimal places", min_value=0, max_value=8, value=4)
allow_negative = st.sidebar.checkbox("Allow negative inputs (for temperatures etc.)", value=True)

# Converter selection
converter = st.selectbox("Choose converter", ("Currency: INR ↔ USD", "Temperature: °C ↔ °F",
                                              "Length: cm ↔ in", "Weight: kg ↔ lb"))

# A small helper to show a swap icon and swap direction
col1, col2 = st.columns([1, 4])
with col1:
    if "swap" not in st.session_state:
        st.session_state.swap = False
    if st.button("🔁 Swap direction"):
        st.session_state.swap = not st.session_state.swap
with col2:
    st.write("Use the Swap button to switch conversion direction.")

# ---------- Currency converter ----------
if converter.startswith("Currency"):
    st.header("Currency — INR ↔ USD")
    # Default exchange rate placeholder; user can edit
    st.write("Rates fluctuate — edit rate below or use a live API (example code commented).")
    inr_per_usd = st.number_input("INR per 1 USD (exchange rate)", value=83.0, format="%.6f",
                                  help="Example: 83 means 1 USD = 83 INR")
    # Optional: show how to fetch live rate (commented sample)
    with st.expander("How to fetch live exchange rate (example)"):
        st.code("""# Example (uncomment and adapt). Requires internet & an API (exchangerate.host is free)
# import requests
# r = requests.get('https://api.exchangerate.host/latest?base=USD&symbols=INR')
# inr_per_usd = r.json()['rates']['INR']
""", language="python")

    if st.session_state.swap is False:
        st.subheader("Convert INR → USD")
        amount_inr = st.number_input("Amount (INR)", value=1000.0, format="%.4f",
                                     min_value=None if allow_negative else 0.0)
        if st.button("Convert INR → USD"):
            usd = inr_to_usd(amount_inr, inr_per_usd)
            st.success(f"₹{fmt(amount_inr, precision)} = ${fmt(usd, precision)} (using {fmt(inr_per_usd,6)} INR/USD)")
    else:
        st.subheader("Convert USD → INR")
        amount_usd = st.number_input("Amount (USD)", value=10.0, format="%.4f",
                                     min_value=None if allow_negative else 0.0)
        if st.button("Convert USD → INR"):
            inr = usd_to_inr(amount_usd, inr_per_usd)
            st.success(f"${fmt(amount_usd, precision)} = ₹{fmt(inr, precision)} (using {fmt(inr_per_usd,6)} INR/USD)")

# ---------- Temperature converter ----------
elif converter.startswith("Temperature"):
    st.header("Temperature — Celsius ↔ Fahrenheit")
    if st.session_state.swap is False:
        st.subheader("Celsius → Fahrenheit")
        c = st.number_input("Temperature (°C)", value=25.0, format="%.4f",
                            min_value=None if allow_negative else 0.0)
        if st.button("Convert °C → °F"):
            f = c_to_f(c)
            st.success(f"{fmt(c, precision)} °C = {fmt(f, precision)} °F")
    else:
        st.subheader("Fahrenheit → Celsius")
        f = st.number_input("Temperature (°F)", value=77.0, format="%.4f",
                            min_value=None if allow_negative else 0.0)
        if st.button("Convert °F → °C"):
            c = f_to_c(f)
            st.success(f"{fmt(f, precision)} °F = {fmt(c, precision)} °C")

# ---------- Length converter ----------
elif converter.startswith("Length"):
    st.header("Length — Centimeter ↔ Inch")
    if st.session_state.swap is False:
        st.subheader("cm → in")
        cm = st.number_input("Length (cm)", value=100.0, format="%.4f",
                             min_value=None if allow_negative else 0.0)
        if st.button("Convert cm → in"):
            inch = cm_to_inch(cm)
            st.success(f"{fmt(cm, precision)} cm = {fmt(inch, precision)} in")
    else:
        st.subheader("in → cm")
        inch = st.number_input("Length (inches)", value=39.3701, format="%.4f",
                               min_value=None if allow_negative else 0.0)
        if st.button("Convert in → cm"):
            cm = inch_to_cm(inch)
            st.success(f"{fmt(inch, precision)} in = {fmt(cm, precision)} cm")

# ---------- Weight converter ----------
elif converter.startswith("Weight"):
    st.header("Weight — Kilogram ↔ Pound")
    if st.session_state.swap is False:
        st.subheader("kg → lb")
        kg = st.number_input("Mass (kg)", value=70.0, format="%.4f",
                             min_value=None if allow_negative else 0.0)
        if st.button("Convert kg → lb"):
            lb = kg_to_lb(kg)
            st.success(f"{fmt(kg, precision)} kg = {fmt(lb, precision)} lb")
    else:
        st.subheader("lb → kg")
        lb = st.number_input("Mass (lb)", value=154.324, format="%.4f",
                             min_value=None if allow_negative else 0.0)
        if st.button("Convert lb → kg"):
            kg = lb_to_kg(lb)
            st.success(f"{fmt(lb, precision)} lb = {fmt(kg, precision)} kg")

# ---------- Footer / usage tips ----------
st.markdown("---")
st.caption("Conversions based on common definitions: 1 in = 2.54 cm; 1 kg = 2.2046226218 lb; °F = °C × 9/5 + 32.")
st.write("Tip: Use the sidebar to change decimal precision and whether negative inputs are allowed.")
