import streamlit as st
from datetime import date, datetime

# Set the page title
st.set_page_config(page_title="Age Calculator", page_icon="🧮", layout="centered")

# App Title
st.title("🧮 Age Calculator")

# Subtitle
st.write("Enter your date of birth to calculate your exact age.")

# Input field for date of birth
dob = st.date_input("Select your Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())

# Button to calculate
if st.button("Calculate Age"):
    today = date.today()
    age_years = today.year - dob.year
    age_months = today.month - dob.month
    age_days = today.day - dob.day

    # Adjust negative months/days
    if age_days < 0:
        age_months -= 1
        previous_month = (today.month - 1) or 12
        year = today.year if today.month > 1 else today.year - 1
        days_in_prev_month = (date(year, previous_month + 1, 1) - date(year, previous_month, 1)).days
        age_days += days_in_prev_month

    if age_months < 0:
        age_years -= 1
        age_months += 12

    # Display results
    st.success(f"🎉 You are **{age_years} years, {age_months} months, and {age_days} days** old.")

# Footer
st.markdown("---")
st.caption("Developed with ❤️ using Streamlit")
