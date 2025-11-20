import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import os

# ---------------------------
#  Config / Helpers
# ---------------------------
DATA_FILE = "workout_log.csv"

# We keep the exercise names (no images shown next to workout name anymore)
EXERCISE_IMAGES = {
    "Bench Press": "C:\\Users\\mural\\Downloads\\Bench_press.png",
    "Squat": "C:\\Users\\mural\\Downloads\\Squat.png",
    "Deadlift": "https://i.imgur.com/2yQm4qF.png",
    "Overhead Press": "https://i.imgur.com/3v7XwPt.png",
    "Barbell Row": "https://i.imgur.com/4fXr6Yk.png",
    "Pull Up": "https://i.imgur.com/6gLwT5K.png",
    "Bicep Curl": "https://i.imgur.com/0Z6v1sF.png",
    "Tricep Dip": "https://i.imgur.com/1a8o9Yz.png",
}

# ---------------------------
#  Background image (Google Drive)
# ---------------------------
# The Drive share link you provided:
# https://drive.google.com/file/d/1xu8fRPtTU9ij-PQca54Iga3VCSOgBN3a/view?usp=sharing
# Use the file id to form a direct view URL:
DRIVE_FILE_ID = "1xu8fRPtTU9ij-PQca54Iga3VCSOgBN3a"
GYM_BG = f"https://drive.google.com/uc?export=view&id={DRIVE_FILE_ID}"

# If you prefer to use a local image instead, set:
# GYM_BG = r"C:\Users\mural\Downloads\your_local_bg.jpg"

st.set_page_config(page_title="Gym Workout Logger", layout="wide")

# Add custom CSS for background and glassy panels
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
  background-image: url('{GYM_BG}');
  background-size: cover;
  background-position: center;
}}
.stCard {{
  background: rgba(255,255,255,0.90);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.2);
}}
.small-muted {{
  color: #555;
  font-size: 0.9rem;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
#  Storage helpers (robust)
# ---------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        # Read as strings first to avoid pandas guessing/raising
        df = pd.read_csv(DATA_FILE, dtype=str, keep_default_na=False)
        # Ensure expected columns exist
        for c in ["date", "exercise", "sets", "reps", "weight", "volume"]:
            if c not in df.columns:
                df[c] = pd.NA
        # Convert date safely (coerce bad values to NaT)
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        # Convert numeric columns safely
        for col in ["sets", "reps", "weight", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    else:
        cols = ["date", "exercise", "sets", "reps", "weight", "volume"]
        return pd.DataFrame(columns=cols)

def save_data(df):
    # Save with ISO date strings for safety
    df_to_save = df.copy()
    if "date" in df_to_save.columns:
        # convert date objects to isoformat strings; leave NaT/NaN as empty
        df_to_save["date"] = df_to_save["date"].apply(lambda d: d.isoformat() if pd.notna(d) else "")
    df_to_save.to_csv(DATA_FILE, index=False)

# ---------------------------
#  UI: Header
# ---------------------------
st.markdown("<div class='stCard'>", unsafe_allow_html=True)
col1, col2 = st.columns([1,3])
with col1:
    # small logo/icon in header (keeps workout input area clean)
    st.image("https://i.imgur.com/3GzQZ6G.png", width=120)
with col2:
    st.title("Gym Workout Logger")
    st.write("Track sets, reps, and weight — see weekly progress and download your logs.")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
#  Input form (removed per-exercise image)
# ---------------------------
st.markdown("<div class='stCard' style='margin-top:12px;'>", unsafe_allow_html=True)
with st.form("log_form"):
    # Use three columns now (exercise, numbers, weight)
    c1, c2, c3 = st.columns([3,2,2])
    with c1:
        exercise = st.selectbox("Workout name", options=list(EXERCISE_IMAGES.keys()), index=0)
        st.markdown("<div class='small-muted'>Pick a common exercise or type your own</div>", unsafe_allow_html=True)
        # If you want to allow free text instead of selectbox, replace above with st.text_input
    with c2:
        sets = st.number_input("Sets", min_value=1, value=3, step=1, format="%d")
        reps = st.number_input("Reps", min_value=1, value=8, step=1, format="%d")
    with c3:
        weight = st.number_input("Weight (kg)", min_value=0.0, value=20.0, step=0.5, format="%.1f")

    date_input = st.date_input("Date", value=date.today())
    submitted = st.form_submit_button("Add log")

if submitted:
    df = load_data()
    entry = {
        "date": pd.to_datetime(date_input).date(),   # store as date object
        "exercise": exercise,
        "sets": int(sets),
        "reps": int(reps),
        "weight": float(weight),
        "volume": int(sets) * int(reps) * float(weight)
    }
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    save_data(df)
    st.success("Log added!")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
#  Load & show logs
# ---------------------------
st.markdown("<div class='stCard' style='margin-top:12px;'>", unsafe_allow_html=True)
logs = load_data()
if logs.empty:
    st.info("No workout logs yet — add your first session above.")
else:
    # logs["date"] is already date objects (or NaT -> NaN) from load_data()
    st.subheader("Your Logs")
    f1, f2, f3 = st.columns([2,2,1])
    with f1:
        exercises_filter = st.multiselect(
            "Filter exercises",
            options=sorted(logs["exercise"].dropna().unique()),
            default=sorted(logs["exercise"].dropna().unique())
        )
    with f2:
        # handle the case where min/max may be NaN
        valid_dates = logs["date"].dropna()
        date_min = valid_dates.min() if len(valid_dates) > 0 else date.today()
        date_max = valid_dates.max() if len(valid_dates) > 0 else date.today()
        date_range = st.date_input("Date range", [date_min, date_max])
    with f3:
        if st.button("Download CSV"):
            st.download_button("Download current logs", logs.to_csv(index=False).encode('utf-8'), file_name="workout_log.csv")

    # Apply filters (guard against NaN dates)
    mask = logs["exercise"].isin(exercises_filter)
    if date_range and len(date_range) == 2:
        start, end = date_range
        mask &= logs["date"].notna() & (logs["date"] >= start) & (logs["date"] <= end)
    filtered = logs[mask].copy()

    st.dataframe(filtered.sort_values(by=["date"], ascending=False).reset_index(drop=True))

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
#  Weekly progress
# ---------------------------
st.markdown("<div class='stCard' style='margin-top:12px;'>", unsafe_allow_html=True)
st.subheader("Weekly Progress")

if not logs.empty and logs["date"].notna().any():
    df = logs.copy()
    # ensure date column is datetime (not string), then compute week_start
    df["date"] = pd.to_datetime(df["date"])
    df["week_start"] = df["date"].dt.to_period('W').apply(lambda r: r.start_time.date() if pd.notna(r) else None)
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
    # Filter out rows with invalid dates for analysis
    df = df[df["week_start"].notna()]

    exercises_available = sorted(df["exercise"].dropna().unique())
    sel = st.multiselect("Select exercises to include in progress", exercises_available, default=exercises_available)

    df_sel = df[df["exercise"].isin(sel)]
    weekly = df_sel.groupby(["week_start"]).agg(total_volume=("volume", "sum")).reset_index()

    if weekly.empty:
        st.info("No data in selected range/exercises to plot.")
    else:
        chart = alt.Chart(weekly).mark_line(point=True).encode(
            x=alt.X('week_start:T', title='Week starting'),
            y=alt.Y('total_volume:Q', title='Total volume (sets × reps × weight)'),
            tooltip=['week_start', 'total_volume']
        ).properties(width=800, height=300)
        st.altair_chart(chart, width='stretch')

    # per-exercise weekly stacked bar
    per_ex = df_sel.groupby(["week_start", "exercise"]).agg(volume=("volume","sum")).reset_index()
    if not per_ex.empty:
        bar = alt.Chart(per_ex).mark_bar().encode(
            x=alt.X('week_start:T', title='Week starting'),
            y=alt.Y('volume:Q', title='Volume'),
            color='exercise:N',
            tooltip=['week_start', 'exercise', 'volume']
        ).properties(width=800, height=300)
        st.altair_chart(bar, width='stretch')

    # Quick stats
    col_a, col_b, col_c = st.columns(3)
    total_vol = df_sel['volume'].sum()
    total_sessions = len(df_sel)
    top_ex = df_sel.groupby('exercise').volume.sum().sort_values(ascending=False)
    with col_a:
        st.metric("Total volume (selected)", f"{total_vol:.1f}")
    with col_b:
        st.metric("Sessions (selected)", f"{total_sessions}")
    with col_c:
        st.metric("Top exercise", top_ex.index[0] if len(top_ex) > 0 else "-")

else:
    st.info("Log workouts to see weekly progress.")

st.markdown("</div>", unsafe_allow_html=True)
