
import streamlit as st
import random
import json
import requests

st.set_page_config(page_title="Surya DISA Quiz", layout="centered")

# Load questions from GitHub
@st.cache_data
def load_questions():
    url = "https://raw.githubusercontent.com/suryaalapati/DISA/main/disa_questions_clean.json"
    response = requests.get(url)
    return response.json()

questions = load_questions()
st.title("Surya DISA Quiz App")
st.markdown("Test your DISA knowledge with random MCQs.")

# Select number of questions
num_qs = st.slider("How many questions do you want?", 1, len(questions), 5)

# Shuffle and limit the questions
random.shuffle(questions)
quiz_questions = questions[:num_qs]

# Initialize session state
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.wrong_qs = []

# Show quiz
if st.session_state.current_q < num_qs:
    q = quiz_questions[st.session_state.current_q]
    st.subheader(f"Q{st.session_state.current_q + 1}: {q['question']}")
    options = q["options"]
    random.shuffle(options)
    choice = st.radio("Choose an option:", options)

    if st.button("Submit"):
        if choice == q["answer"]:
            st.success("Correct!")
            st.session_state.score += 1
        else:
            st.error(f"Wrong. The correct answer is: {q['answer']}")
            st.session_state.wrong_qs.append(q)

        st.session_state.current_q += 1
        st.experimental_rerun()
else:
    st.success(f"Quiz complete! You scored {st.session_state.score}/{num_qs}")
    if st.session_state.wrong_qs:
        if st.button("Retry Wrong Questions"):
            quiz_questions = st.session_state.wrong_qs
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.wrong_qs = []
            st.experimental_rerun()

    if st.button("Restart Quiz"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.wrong_qs = []
        st.experimental_rerun()
