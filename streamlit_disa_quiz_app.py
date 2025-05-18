
import streamlit as st
import random
import json
import requests
import time

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
    st.session_state.start_time = time.time()

# Show quiz
if st.session_state.current_q < num_qs:
    q = quiz_questions[st.session_state.current_q]
    st.subheader(f"Q{st.session_state.current_q + 1}: {q['question']}")

    options = [f"A. {q.get('a', '')}", f"B. {q.get('b', '')}", f"C. {q.get('c', '')}", f"D. {q.get('d', '')}"]
    choice = st.radio("Choose an option:", options)

    if st.button("Submit"):
        correct_option = q.get("correct", "").upper()
        correct_answer_text = q.get(correct_option.lower(), "")
        explanation = q.get("explanation", "No explanation provided.")

        selected_letter = choice.split(".")[0].strip().upper()

        if selected_letter == correct_option:
            st.success("Correct!")
            st.session_state.score += 1
        else:
            st.error(f"Wrong. The correct answer is: {correct_option}. {correct_answer_text}")
            st.info(f"Explanation: {explanation}")
            st.session_state.wrong_qs.append(q)

        st.session_state.current_q += 1
        st.experimental_rerun()
else:
    end_time = time.time()
    total_time = round(end_time - st.session_state.start_time, 2)
    st.success(f"Quiz complete! You scored {st.session_state.score}/{num_qs}")
    st.info(f"⏱ Total Time Taken: {total_time} seconds")

    if st.session_state.wrong_qs:
        st.subheader("❌ Review Your Wrong Answers:")
        for idx, wrong_q in enumerate(st.session_state.wrong_qs, 1):
            correct_option = wrong_q.get("correct", "").upper()
            correct_answer_text = wrong_q.get(correct_option.lower(), "")
            explanation = wrong_q.get("explanation", "No explanation provided.")
            st.markdown(f"**Q{idx}: {wrong_q['question']}**")
            st.markdown(f"✅ Correct Answer: {correct_option}. {correct_answer_text}")
            st.markdown(f"📘 Explanation: {explanation}")
            st.markdown("---")

        if st.button("Retry Wrong Questions"):
            quiz_questions = st.session_state.wrong_qs
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.wrong_qs = []
            st.session_state.start_time = time.time()
            st.experimental_rerun()

    if st.button("Restart Quiz"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.wrong_qs = []
        st.session_state.start_time = time.time()
        st.experimental_rerun()
