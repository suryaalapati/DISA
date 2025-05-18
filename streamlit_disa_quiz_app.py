
import streamlit as st
import json
import random
import time

st.set_page_config(page_title="Surya DISA Quiz App", layout="centered")

# Load from local JSON
with open("disa_questions_clean_final.json", "r", encoding="utf-8") as f:
    all_questions = json.load(f)

# Filter fully valid ones
questions = [
    {k.lower(): v for k, v in q.items()}
    for q in all_questions
    if all(k in q for k in ["a", "b", "c", "d", "correct", "question"])
]

# Session state setup
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "selected" not in st.session_state:
    st.session_state.selected = None
if "wrong_qs" not in st.session_state:
    st.session_state.wrong_qs = []

username = st.text_input("Enter your name to begin:")
num_qs = st.slider("How many questions?", 1, len(questions), 5)
if st.button("Start Quiz") and username:
    st.session_state.quiz_started = True
    st.session_state.selected = None
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.wrong_qs = []
    st.session_state.qs = random.sample(questions, num_qs)
    st.session_state.start_time = time.time()

if st.session_state.quiz_started:
    idx = st.session_state.current_q
    total = len(st.session_state.qs)
    if idx < total:
        q = st.session_state.qs[idx]
        clean_qtext = q["question"].replace("\n", " ").replace("
", " ").strip()
        st.markdown(f"### **Q{idx + 1}/{total}: {clean_qtext}**")

        options = [f"A. {q['a']}", f"B. {q['b']}", f"C. {q['c']}", f"D. {q['d']}"]
        choice = st.radio("Choose an option:", options, index=None)

        if st.button("Submit Answer"):
            selected_letter = choice[0].lower() if choice else ""
            correct_letter = q["correct"].strip().lower()
            st.session_state.selected = selected_letter

            if selected_letter == correct_letter:
                st.success(f"✅ Correct! {choice}")
                st.session_state.score += 1
            else:
                correct_text = q[correct_letter]
                st.error(f"❌ Wrong. The correct answer is: {correct_letter.upper()}. {correct_text}")
            st.info(f"📘 Explanation: {q.get('explanation', 'No explanation provided.')}")

        if st.session_state.selected and st.button("Next Question"):
            if st.session_state.selected != q["correct"]:
                st.session_state.wrong_qs.append(q)
            st.session_state.current_q += 1
            st.session_state.selected = None
            st.rerun()

    else:
        duration = round(time.time() - st.session_state.start_time, 2)
        st.success(f"🎉 Done! Score: {st.session_state.score}/{total} in {duration} seconds.")
        if st.session_state.wrong_qs:
            st.markdown("### ❌ Review Wrong Answers")
            for wq in st.session_state.wrong_qs:
                st.write("Q:", wq["question"])
                correct_letter = wq["correct"].lower()
                st.write(f"✅ Correct: {correct_letter.upper()}. {wq[correct_letter]}")
                st.write("📘 Explanation:", wq.get("explanation", "-"))
                st.markdown("---")
