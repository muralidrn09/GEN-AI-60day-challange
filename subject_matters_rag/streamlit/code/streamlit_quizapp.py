import streamlit as st
import random

st.set_page_config(page_title="General Knowledge Quiz", page_icon="❓", layout="centered")

QUESTIONS = [
    {
        "question": "What is the largest planet in our solar system?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Jupiter"
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "options": ["William Shakespeare", "Charles Dickens", "Leo Tolstoy", "Mark Twain"],
        "answer": "William Shakespeare"
    },
    {
        "question": "Which element has the chemical symbol 'O'?",
        "options": ["Gold", "Oxygen", "Osmium", "Zinc"],
        "answer": "Oxygen"
    },
    {
        "question": "What is the capital of Japan?",
        "options": ["Seoul", "Tokyo", "Kyoto", "Osaka"],
        "answer": "Tokyo"
    },
    {
        "question": "Which continent is the Sahara Desert located on?",
        "options": ["Asia", "Africa", "South America", "Australia"],
        "answer": "Africa"
    },
    {
        "question": "In computing, what does 'CPU' stand for?",
        "options": ["Central Process Unit", "Central Processing Unit", "Computer Personal Unit", "Control Processing Unit"],
        "answer": "Central Processing Unit"
    },
    {
        "question": "Which ocean is the largest by surface area?",
        "options": ["Atlantic Ocean", "Arctic Ocean", "Indian Ocean", "Pacific Ocean"],
        "answer": "Pacific Ocean"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Claude Monet", "Pablo Picasso", "Leonardo da Vinci"],
        "answer": "Leonardo da Vinci"
    },
    {
        "question": "Which country hosted the 2016 Summer Olympics?",
        "options": ["China", "Brazil", "United Kingdom", "Russia"],
        "answer": "Brazil"
    },
    {
        "question": "Which gas do plants primarily absorb from the atmosphere for photosynthesis?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "answer": "Carbon Dioxide"
    }
]

# -----------------------
# Session state init
# -----------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "order" not in st.session_state:
    st.session_state.order = list(range(len(QUESTIONS)))
if "answers" not in st.session_state:
    # store user's chosen option per question index: None if not answered
    st.session_state.answers = {i: None for i in range(len(QUESTIONS))}
if "finished" not in st.session_state:
    st.session_state.finished = False

# -----------------------
# Helper functions
# -----------------------
def start_quiz(shuffle: bool):
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.finished = False
    st.session_state.answers = {i: None for i in range(len(QUESTIONS))}
    st.session_state.order = list(range(len(QUESTIONS)))
    if shuffle:
        random.shuffle(st.session_state.order)

def submit_answer(selected):
    idx = st.session_state.order[st.session_state.q_index]
    st.session_state.answers[idx] = selected

def next_question():
    if st.session_state.q_index < len(QUESTIONS) - 1:
        st.session_state.q_index += 1

def prev_question():
    if st.session_state.q_index > 0:
        st.session_state.q_index -= 1

def finish_quiz():
    # calculate score
    score = 0
    for i, q in enumerate(QUESTIONS):
        chosen = st.session_state.answers.get(i)
        if chosen is not None and chosen == q["answer"]:
            score += 1
    st.session_state.score = score
    st.session_state.finished = True

# -----------------------
# UI: Header and controls
# -----------------------
st.title("❓ General Knowledge Quiz")
st.write("Test your general knowledge. Choose the correct option for each question.")

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("Restart (no shuffle)"):
        start_quiz(shuffle=False)
with col2:
    if st.button("Restart & Shuffle"):
        start_quiz(shuffle=True)
with col3:
    st.write(f"Question {st.session_state.q_index + 1} / {len(QUESTIONS)}")

progress = (st.session_state.q_index + 1) / len(QUESTIONS)
st.progress(progress)

st.markdown("---")

# -----------------------
# Show question (unless finished)
# -----------------------
if not st.session_state.finished:
    q_idx = st.session_state.order[st.session_state.q_index]
    q = QUESTIONS[q_idx]

    st.subheader(f"Q{st.session_state.q_index + 1}: {q['question']}")
    # Use a form to avoid immediate widget-changing reruns
    with st.form(key=f"form_{q_idx}"):
        # shuffle options locally so the correct answer doesn't always appear in same position
        opts = q["options"].copy()
        # Keep deterministic per session question display order:
        random.seed(q_idx + len(st.session_state.order))  # slight deterministic randomness
        random.shuffle(opts)

        selected = st.radio("Choose one:", opts, index=opts.index(st.session_state.answers[q_idx]) if st.session_state.answers[q_idx] in opts else 0)
        submitted = st.form_submit_button("Save Answer")
        if submitted:
            submit_answer(selected)
            st.success("Answer saved ✅")

    # Navigation buttons
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])
    with nav_col1:
        if st.button("Previous"):
            prev_question()
    with nav_col2:
        if st.button("Next"):
            next_question()
    with nav_col3:
        if st.button("Finish Quiz"):
            finish_quiz()
    with nav_col4:
        st.write("")  # spacer

    # Quick review of current selection
    user_choice = st.session_state.answers[q_idx]
    if user_choice:
        st.info(f"Your saved answer for this question: **{user_choice}**")

else:
    # -----------------------
    # Results screen
    # -----------------------
    st.success("🎉 Quiz Completed!")
    st.write(f"Your score: **{st.session_state.score} / {len(QUESTIONS)}**")
    percent = st.session_state.score / len(QUESTIONS) * 100
    st.write(f"Percentage: **{percent:.1f}%**")

    st.markdown("### Review answers")
    for i, q in enumerate(QUESTIONS):
        chosen = st.session_state.answers.get(i)
        correct = q["answer"]
        status = "✅ Correct" if chosen == correct else "❌ Incorrect"
        st.write(f"**Q{i+1}. {q['question']}**")
        st.write(f"- Your answer: **{chosen}**")
        st.write(f"- Correct answer: **{correct}** — {status}")
        st.markdown("---")

    if st.button("Try Again (Shuffle)"):
        start_quiz(shuffle=True)

# Footer
st.caption("Built with Streamlit — customize the question bank to fit your audience!")
