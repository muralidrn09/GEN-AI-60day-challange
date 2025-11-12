# trip_expense_splitter.py
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Expense Splitter", layout="centered")

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
    background: rgba(255, 255, 255, 0.10);  /* lighter transparency */
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

# -----------------------
# Helper functions
# -----------------------
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "members" not in st.session_state:
        st.session_state.members = []  # list of member names (original-cased)
    if "members_norm" not in st.session_state:
        # parallel set to check duplicates quickly (lowercase trimmed)
        st.session_state.members_norm = set()
    if "expenses" not in st.session_state:
        # each expense: dict {name, amount (float), payer, splits (dict name->float)}
        st.session_state.expenses = []
    if "trip_from" not in st.session_state:
        st.session_state.trip_from = None
    if "trip_to" not in st.session_state:
        st.session_state.trip_to = None
    # initialize the input bound key BEFORE widget creation (prevents StreamlitAPIException)
    if "new_member" not in st.session_state:
        st.session_state.new_member = ""
    if "_tmp_msg" not in st.session_state:
        st.session_state._tmp_msg = ""

def normalize_name(n: str) -> str:
    return n.strip().lower()

def add_member(name: str):
    """Add member with duplicate prevention (case-insensitive)."""
    name_stripped = name.strip()
    if not name_stripped:
        st.warning("Enter a non-empty name.")
        return False
    n_norm = normalize_name(name_stripped)
    if n_norm in st.session_state.members_norm:
        st.warning(f"'{name_stripped}' already added.")
        return False
    st.session_state.members.append(name_stripped)
    st.session_state.members_norm.add(n_norm)
    return True

def remove_member(name: str):
    """Remove a single member and all expenses where they were the payer."""
    if name in st.session_state.members:
        st.session_state.members.remove(name)
        st.session_state.members_norm.discard(normalize_name(name))
        # remove any expenses where payer removed
        st.session_state.expenses = [e for e in st.session_state.expenses if e["payer"] != name]

def remove_members_bulk(names: list):
    """Remove multiple selected members."""
    for n in names:
        remove_member(n)

def add_expense(expense_name, amount, payer, split_equally, custom_splits):
    try:
        amount = float(amount)
    except:
        st.error("Amount must be a number.")
        return False
    if payer not in st.session_state.members:
        st.error("Payer must be one of the members.")
        return False
    if amount <= 0:
        st.error("Enter amount > 0.")
        return False

    if split_equally:
        per_person = round(amount / len(st.session_state.members), 2) if st.session_state.members else 0.0
        splits = {m: per_person for m in st.session_state.members}
        # adjust due to rounding: add remainder to payer
        remainder = round(amount - sum(splits.values()), 2)
        if remainder:
            splits[payer] = round(splits[payer] + remainder, 2)
    else:
        # custom_splits should be a dict mapping names to amounts (numbers)
        splits = {}
        total_custom = 0.0
        for m in st.session_state.members:
            s = custom_splits.get(m, 0.0) if custom_splits else 0.0
            try:
                s_val = float(s)
            except:
                s_val = 0.0
            splits[m] = round(s_val, 2)
            total_custom += s_val
        total_custom = round(total_custom, 2)
        if round(total_custom, 2) != round(amount, 2):
            st.error(f"Custom splits sum ({total_custom}) does not equal amount ({amount}).")
            return False

    st.session_state.expenses.append({
        "name": expense_name,
        "amount": round(amount,2),
        "payer": payer,
        "splits": splits
    })
    st.success(f"Added expense '{expense_name}' of {amount} paid by {payer}.")
    return True

def calculate_net_balances():
    # returns dict member -> net_balance (positive => should receive money; negative => owes)
    balances = {m: 0.0 for m in st.session_state.members}
    for e in st.session_state.expenses:
        amt = e["amount"]
        payer = e["payer"]
        splits = e["splits"]
        balances[payer] += amt
        for m, s in splits.items():
            balances[m] -= s
    balances = {m: round(b,2) for m,b in balances.items()}
    return balances

def settle_balances(balances):
    # Greedy settlement algorithm
    transactions = []
    bal = {p: round(balances[p],2) for p in balances}
    creditors = [(p, bal[p]) for p in bal if bal[p] > 0]
    debtors = [(p, bal[p]) for p in bal if bal[p] < 0]
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])  # most negative first
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt_amount = debtors[i]
        creditor, cred_amount = creditors[j]
        pay = min(round(cred_amount,2), round(-debt_amount,2))
        if pay <= 0.0:
            break
        transactions.append({"from": debtor, "to": creditor, "amount": round(pay,2)})
        debt_amount += pay
        cred_amount -= pay
        debtors[i] = (debtor, round(debt_amount,2))
        creditors[j] = (creditor, round(cred_amount,2))
        if abs(debtors[i][1]) < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1
    return transactions

# -----------------------
# Initialize
# -----------------------
init_session()

# -----------------------
# Login Page
# -----------------------
st.title("Expense Splitter")

if not st.session_state.logged_in:
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    # Hard-coded credentials (replace with secure system in production)
    COMMON_USERNAME = "tripuser"
    COMMON_PASSWORD = "letspyth0n"
    if submitted:
        if username == COMMON_USERNAME and password == COMMON_PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password. Try 'tripuser' / 'letspyth0n' for demo.")

    st.info("Demo credentials: username `tripuser` and password `letspyth0n`")
    st.stop()

# -----------------------
# Main App (after login)
# -----------------------
st.header("Trip Planner & Expense Splitter")

# Trip dates
col1, col2 = st.columns(2)
with col1:
    trip_from = st.date_input("Trip from", value=st.session_state.trip_from or date.today())
with col2:
    trip_to = st.date_input("Trip to", value=st.session_state.trip_to or date.today())

# Save trip dates to session
st.session_state.trip_from = trip_from
st.session_state.trip_to = trip_to

st.markdown(f"**Trip period:** {st.session_state.trip_from} → {st.session_state.trip_to}")

# -----------------------
# Members management
# -----------------------
st.subheader("Group members")
member_col1, member_col2 = st.columns([3,1])

# Callback for adding member (safe to mutate session_state)
def add_member_callback():
    name = st.session_state.get("new_member", "").strip()
    if not name:
        st.session_state._tmp_msg = "Enter a non-empty name."
        return
    # check duplicates case-insensitively
    if normalize_name(name) in st.session_state.members_norm:
        st.session_state._tmp_msg = f"'{name}' is already in the list."
        # clear input
        st.session_state.new_member = ""
        return
    # append
    st.session_state.members.append(name)
    st.session_state.members_norm.add(normalize_name(name))
    st.session_state.new_member = ""
    st.session_state._tmp_msg = f"Added '{name}'"

with member_col1:
    st.text_input("Add member (enter name and click +)", key="new_member")

with member_col2:
    st.button("+ Add member", on_click=add_member_callback, key="add_member_btn")

# Show temporary messages
if st.session_state._tmp_msg:
    msg = st.session_state._tmp_msg
    st.session_state._tmp_msg = ""  # clear
    if msg.startswith("Added"):
        st.success(msg)
    else:
        st.warning(msg)

# Show members list and provide remove options
if st.session_state.members:
    members_df = pd.DataFrame({"Member": st.session_state.members})
    st.table(members_df)

    with st.expander("Remove members"):
        # allow selection of one or more members to remove
        to_remove = st.multiselect("Select members to remove", options=st.session_state.members, key="to_remove_sel")
        if to_remove and st.button("Remove selected"):
            remove_members_bulk(to_remove)
            st.rerun()

    # Also provide a dedupe button if duplicates somehow exist
    if st.button("Remove duplicate entries (if any)"):
        # re-create members list while preserving first occurrences
        seen = set()
        new_members = []
        for m in st.session_state.members:
            n = normalize_name(m)
            if n not in seen:
                seen.add(n)
                new_members.append(m)
        st.session_state.members = new_members
        st.session_state.members_norm = set(normalize_name(m) for m in new_members)
        st.success("Duplicates (if any) removed.")
        st.rerun()
else:
    st.info("Add members to the trip. Use the + Add member button.")

# -----------------------
# Expenses
# -----------------------
# -----------------------
# Expenses (fixed — uses session_state-bound widgets + on_click callback)
# -----------------------
st.subheader("Add Expense")
if not st.session_state.members:
    st.info("Please add members before adding expenses.")
else:
    # --- Ensure keys exist BEFORE widget creation ---
    if "e_name" not in st.session_state:
        st.session_state.e_name = "Lunch"
    if "e_amount" not in st.session_state:
        st.session_state.e_amount = 0.0
    # default payer to first member if not set or no longer valid
    if "e_payer" not in st.session_state or st.session_state.e_payer not in st.session_state.members:
        st.session_state.e_payer = st.session_state.members[0]
    if "split_choice" not in st.session_state:
        st.session_state.split_choice = "Split equally"
    # ensure custom inputs exist for every member (create keys BEFORE widgets)
    for m in st.session_state.members:
        k = f"custom_{m}"
        if k not in st.session_state:
            st.session_state[k] = 0.0

    # Callback that will run inside the widget (allowed to mutate session_state)
    def expense_form_submit_cb():
        e_name = st.session_state.get("e_name", "").strip()
        e_amount = st.session_state.get("e_amount", 0.0)
        e_payer = st.session_state.get("e_payer")
        split_choice = st.session_state.get("split_choice", "Split equally")
        split_equally = (split_choice == "Split equally")

        # build custom_splits dict from session_state keys if needed
        custom_splits = {}
        if not split_equally:
            for m in st.session_state.members:
                custom_splits[m] = st.session_state.get(f"custom_{m}", 0.0)

        # call your existing add_expense helper
        success = add_expense(e_name, e_amount, e_payer, split_equally, custom_splits)
        if success:
            # Clear form fields — allowed because we're inside callback
            st.session_state.e_name = ""
            st.session_state.e_amount = 0.0
            # reset custom inputs
            for m in st.session_state.members:
                st.session_state[f"custom_{m}"] = 0.0
            # optionally reset split method
            st.session_state.split_choice = "Split equally"
            # rerun to refresh UI (safe)
            st.rerun()

    # --- The form (binds inputs to session_state keys) ---
    with st.form("expense_form"):
        st.text_input("Expense name", key="e_name")
        st.number_input("Amount (INR)", min_value=0.0, format="%.2f", step=0.5, key="e_amount")
        st.selectbox("Payer", options=st.session_state.members, key="e_payer")
        st.radio("Split method", options=["Split equally", "Custom split"], index=0, key="split_choice")

        # Show custom inputs only if the radio says "Custom split".
        # Note: the widget still exists in the form but we only populate/use custom values when required.
        if st.session_state.split_choice == "Custom split":
            st.markdown("Enter per-member share (must sum to total amount).")
            for m in st.session_state.members:
                st.number_input(f"Amount for {m}", min_value=0.0, format="%.2f", step=0.5, key=f"custom_{m}")

        # Submit button tied to our callback
        st.form_submit_button("Add expense", on_click=expense_form_submit_cb)


# -----------------------
# Expenses table & settlement (with delete checkboxes)
# -----------------------
st.subheader("Expenses & Settlement")

def _expense_display_text(idx, e):
    # A concise string to identify the expense in checkboxes
    return f"{idx+1}. {e['name']} — ₹{e['amount']:.2f} (paid by {e['payer']})"

if st.session_state.expenses:
    # Build a display table for the UI
    exp_table = []
    for e in st.session_state.expenses:
        splits_str = "; ".join([f"{k}: {v}" for k,v in e["splits"].items()])
        exp_table.append({"Expense": e["name"], "Amount": e["amount"], "Payer": e["payer"], "Splits": splits_str})
    st.table(pd.DataFrame(exp_table))

    st.markdown("### Select expenses to delete")
    # Create checkboxes for each expense (keyed by index for stability)
    selected_indices = []
    for i, e in enumerate(st.session_state.expenses):
        key = f"exp_chk_{i}"
        checked = st.checkbox(_expense_display_text(i, e), key=key)
        if checked:
            selected_indices.append(i)

    # Delete selected button (removes the selected expense entries)
    if st.button("Delete selected expenses"):
        if not selected_indices:
            st.warning("No expenses selected to delete.")
        else:
            # remove by index (remove from highest index to lowest to avoid reindexing issues)
            for idx in sorted(selected_indices, reverse=True):
                # safety check
                if 0 <= idx < len(st.session_state.expenses):
                    removed = st.session_state.expenses.pop(idx)
                    # optionally show info for each removed
                    st.info(f"Removed: {removed['name']} — ₹{removed['amount']:.2f} (paid by {removed['payer']})")
            # After deletion, clear any leftover checkbox keys and rerun to refresh UI
            st.rerun()

    # Show balances and settlements
    balances = calculate_net_balances()
    st.markdown("**Net balances (positive → should receive; negative → owes):**")
    bal_df = pd.DataFrame.from_dict(balances, orient="index", columns=["Net Balance"]).reset_index().rename(columns={"index":"Member"})
    st.table(bal_df)

    st.markdown("**Suggested payments to settle up:**")
    txns = settle_balances(balances)
    if txns:
        tx_df = pd.DataFrame(txns)
        st.table(tx_df)
    else:
        st.info("No settlements needed. All settled or no expenses.")

    # Reset all data button
    if st.button("Reset all data"):
        st.session_state.members = []
        st.session_state.members_norm = set()
        st.session_state.expenses = []
        st.session_state.trip_from = None
        st.session_state.trip_to = None
        st.rerun()
else:
    st.info("No expenses recorded yet. Add expenses above.")
