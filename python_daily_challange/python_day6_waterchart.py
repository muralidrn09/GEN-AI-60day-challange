import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import altair as alt
import os

DB_PATH = "water_db.sqlite"

# ----------------- Database helpers -----------------

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS water_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount_ml INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_entry(entry_date: str, amount_ml: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO water_logs (date, amount_ml) VALUES (?, ?)",
        (entry_date, int(amount_ml)),
    )
    conn.commit()
    conn.close()


def delete_entries(ids: list):
    if not ids:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM water_logs WHERE id IN ({','.join(['?']*len(ids))})", ids)
    conn.commit()
    conn.close()


def fetch_all_records() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM water_logs ORDER BY date DESC, created_at DESC", conn)
    conn.close()
    if df.empty:
        return pd.DataFrame(columns=["id", "date", "amount_ml", "created_at"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def get_daily_total(target_date: date) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount_ml) FROM water_logs WHERE date = ?", (target_date.isoformat(),))
    res = cur.fetchone()[0]
    conn.close()
    return int(res or 0)


def get_weekly_totals(reference_date: date = None) -> pd.DataFrame:
    if reference_date is None:
        reference_date = date.today()
    start = reference_date - timedelta(days=6)
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT date, SUM(amount_ml) as total_ml FROM water_logs WHERE date BETWEEN ? AND ? GROUP BY date",
        conn,
        params=(start.isoformat(), reference_date.isoformat()),
    )
    conn.close()

    # Build full 7-day frame with zeros where no data
    days = [start + timedelta(days=i) for i in range(7)]
    df_full = pd.DataFrame({"date": [d for d in days]})
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df_full = df_full.merge(df, on="date", how="left")
        df_full["total_ml"] = df_full["total_ml"].fillna(0).astype(int)
    else:
        df_full["total_ml"] = 0

    return df_full


# ----------------- UI & App logic -----------------

st.set_page_config(page_title="Water Intake Tracker", page_icon="💧", layout="centered")

init_db()

st.title("💧 Water Intake Tracker")
st.markdown("Log your daily water (ml). Progress shown to your daily goal (default 3 L). See weekly hydration chart.")

# Sidebar: settings
with st.sidebar:
    st.header("Settings")
    default_goal = 3000
    goal_ml = st.number_input("Daily goal (ml)", min_value=500, max_value=10000, value=default_goal, step=100)
    st.write("Tip: 3000 ml = 3 liters")
    st.markdown("---")
    #st.write("Database file:"
    #st.write(os.path.abspath(DB_PATH))

# Input section
st.header("Add water intake")
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    amount = st.number_input("Amount (ml)", min_value=10, max_value=10000, value=250, step=10)
with col2:
    entry_date = st.date_input("Date", value=date.today())
with col3:
    add_btn = st.button("Add")

if add_btn:
    add_entry(entry_date.isoformat(), int(amount))
    st.success(f"Added {amount} ml for {entry_date.isoformat()}")

# Today's summary
st.header("Today's summary")
today = date.today()
selected_date = st.date_input("View entries for date", value=today, key="view_date")

today_total = get_daily_total(selected_date)
progress = min(today_total / goal_ml, 1.0) if goal_ml > 0 else 0

colA, colB, colC = st.columns(3)
colA.metric("Total today (ml)", f"{today_total} ml")
colB.metric("Remaining (ml)", f"{max(goal_ml - today_total, 0)} ml")
colC.metric("% of goal", f"{int(progress * 100)}%")

st.progress(progress)

# Show entries for selected_date with ability to delete
all_records = fetch_all_records()
if all_records.empty:
    st.info("No records yet. Add your first water intake above.")
else:
    records_for_date = all_records[all_records["date"] == selected_date]
    if records_for_date.empty:
        st.write("No entries for this date.")
    else:
        st.subheader("Entries")
        # show a table with an index we can use to delete
        display_df = records_for_date.copy()
        display_df = display_df[["id", "date", "amount_ml", "created_at"]]
        display_df["created_at"] = pd.to_datetime(display_df["created_at"]) 
        display_df = display_df.sort_values(by="created_at", ascending=False)
        selected_ids = st.multiselect("Select entries to delete (check and click 'Delete selected')", options=display_df["id"].tolist(), format_func=lambda x: f"ID {x} - {display_df[display_df['id']==x].iloc[0]['amount_ml']} ml @ {display_df[display_df['id']==x].iloc[0]['created_at']}")
        st.dataframe(display_df.rename(columns={"id": "ID", "date": "Date", "amount_ml": "Amount (ml)", "created_at": "Logged at"}))
        if st.button("Delete selected"):
            if selected_ids:
                delete_entries([str(i) for i in selected_ids])
                st.success(f"Deleted {len(selected_ids)} entries")
            else:
                st.warning("No entries selected to delete.")

# Weekly hydration chart
st.header("Weekly hydration (last 7 days)")
weekly_df = get_weekly_totals(reference_date=selected_date)
# Prepare for chart
chart_df = pd.DataFrame({
    "date": pd.to_datetime(weekly_df["date"]),
    "total_ml": weekly_df["total_ml"],
})

bars = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('total_ml:Q', title='Total water (ml)'),
    tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('total_ml:Q', title='Total (ml)')]
)

rule = alt.Chart(pd.DataFrame({'y': [goal_ml]})).mark_rule(strokeDash=[4,4]).encode(
    y='y:Q'
)

st.altair_chart((bars + rule).properties(width=700, height=350), use_container_width=True)

# Export all records
st.header("Data & export")
all_records = fetch_all_records()
if all_records.empty:
    st.write("No data to export.")
else:
    st.dataframe(all_records.rename(columns={"id": "ID", "date": "Date", "amount_ml": "Amount (ml)", "created_at": "Logged at"}))
    csv = all_records.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="water_logs.csv", mime="text/csv")