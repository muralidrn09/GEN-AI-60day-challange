from datetime import date

import streamlit as st

# ------------------ Page Config ------------------
st.set_page_config(page_title="Greeting & Discount App", page_icon="🎉")

# ------------------ Transparent Background Styling ------------------
page_bg = """
<style>
/* --- Main App Background --- */
[data-testid="stAppViewContainer"] {
    background-color: rgba(255, 255, 255, 0.15); /* very light transparent white */
    background-image: linear-gradient(
        rgba(255, 255, 255, 0.1),
        rgba(255, 255, 255, 0.1)
    ),
    url("https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1400&q=60");
    background-size: cover;
    background-position: center;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    border-right: 1px solid rgba(255,255,255,0.2);
}

/* --- Main Content Area --- */
.main {
    background: rgba(255, 255, 255, 0.18);  /* lighter transparency */
    backdrop-filter: blur(8px);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0px 0px 5px rgba(0,0,0,0.05);  /* very subtle shadow */
}

/* --- Headings & Text for Contrast --- */
h1, h2, h3, label, p, span {
    color: #111 !important;
    font-weight: 500;
}

/* --- Buttons --- */
div.stButton > button {
    background-color: rgba(0, 122, 255, 0.85);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6em 1.2em;
    font-weight: 600;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    background-color: rgba(0, 122, 255, 1.0);
    transform: scale(1.02);
}

/* --- Inputs and Sliders --- */
input, .stSlider {
    color: #000 !important;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# ------------------ Helpers ------------------
def calculate_age(birthdate: date, today: date) -> int:
    years = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years


def birthdate_from_age(age: int, today: date) -> date:
    try:
        return date(today.year - age, today.month, today.day)
    except ValueError:
        return date(today.year - age, 2, 28)  # handle Feb 29 fallback


def get_discount_by_age(age: int):
    if age <= 12:
        return 40, "Kids Offer"
    elif 13 <= age <= 19:
        return 25, "Teen Offer"
    elif 20 <= age <= 59:
        return 10, "Adults Offer"
    else:
        return 50, "Senior Citizen Offer"


# ------------------ Page Title ------------------
st.title("🎉 Greeting & Age-based Discount Form")
st.write(
    "Pick your birth date — the age slider will update automatically. "
    "Submit to see your personalized greeting and discount offer."
)

# ------------------ Session State ------------------
today = date.today()
if "birthdate" not in st.session_state:
    st.session_state.birthdate = birthdate_from_age(25, today)
if "age" not in st.session_state:
    st.session_state.age = calculate_age(st.session_state.birthdate, today)


# ------------------ Callbacks ------------------
def on_birthdate_change():
    bd = st.session_state.birthdate
    st.session_state.age = calculate_age(bd, today)


def on_age_change():
    a = st.session_state.age
    st.session_state.birthdate = birthdate_from_age(a, today)


# ------------------ Controls ------------------
st.date_input(
    "📅 Select your birth date",
    value=st.session_state.birthdate,
    max_value=today,
    key="birthdate",
    on_change=on_birthdate_change,
)

st.slider(
    "🎚️ Select your age",
    min_value=0,
    max_value=120,
    value=st.session_state.age,
    key="age",
    on_change=on_age_change,
)

st.write("---")

# ------------------ Form ------------------
with st.form("greeting_form"):
    name = st.text_input("👤 Enter your name", placeholder="Type your name here")
    submitted = st.form_submit_button("✨ Submit")

# ------------------ Submit Handler ------------------
# (Keep all your earlier logic here...)

if submitted:
    cleaned_name = name.strip().title() if name.strip() else "Guest"
    final_birthdate = st.session_state.birthdate
    final_age = calculate_age(final_birthdate, today)
    discount, category = get_discount_by_age(final_age)

    popup_html = f"""
    <div style="
        position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%);
        background: rgba(255,255,255,0.95);
        color: #000;
        border-radius: 12px;
        padding: 25px 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        z-index: 9999;
        text-align: center;
        font-size: 18px;">
        <p>👋 <b>Welcome, Mr. {cleaned_name}!</b></p>
        <p>🎂 You are {final_age} years old<br>(Born on {final_birthdate.strftime("%d %B %Y")}).</p>
        <p>🛍️ You are eligible for a <b>{discount}% discount</b><br>under the <b>{category}</b> category!</p>
    </div>

    <script>
        setTimeout(function(){{
        var popup = document.getElementById('popupBox');
        if (popup) {{
            popup.style.transition = 'opacity 0.5s ease';
            popup.style.opacity = '0';
            setTimeout(function() {{
                popup.remove();
            }}, 500);
        }}
    }}, 5000);
    </script>
    """
    st.markdown(popup_html, unsafe_allow_html=True)
