
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
st.title("🎓 Surya DISA Quiz App")
st.markdown("Test your DISA knowledge with random MCQs.")

# Leaderboard stored in session
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []

username = st.text_input("Enter your name to appear on the leaderboard:")
num_qs = st.slider("🧠 How many questions do you want?", 1, len(questions), 5)
start_button = st.button("Start Quiz")

# Init state
for key in ["quiz_started", "current_q", "score", "wrong_qs", "start_time", "quiz_questions", "submitted", "last_choice"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key in ["current_q", "score"] else [] if key == "wrong_qs" else False if key == "quiz_started" else None

# Start
if start_button and username:
    st.session_state.quiz_started = True
    st.session_state.quiz_questions = random.sample(questions, num_qs)
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.wrong_qs = []
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.session_state.last_choice = ""

if st.session_state.quiz_started and st.session_state.quiz_questions:
    quiz_questions = st.session_state.quiz_questions
    current_index = st.session_state.current_q
    total_questions = len(quiz_questions)

    if current_index < total_questions:
        q = quiz_questions[current_index]
        st.markdown(f"### **Q{current_index + 1}/{total_questions}: {q.get('question', '⚠️ Question missing')}**")

        # Display all 4 options directly
        choices = ["a", "b", "c", "d"]
        option_labels = [f"{ch.upper()}. {q.get(ch, f'⚠️ Option {ch.upper()} missing')}" for ch in choices]
        selected = st.radio("Choose an option:", option_labels, index=None, key=f"q{current_index}")

        if st.button("Submit Answer") or st.session_state.submitted:
            correct_key = q.get("correct", "").strip().lower()
            selected_letter = selected.split(".")[0].strip().lower() if selected else ""
            correct_text = q.get(correct_key, "⚠️ Correct answer text missing")
            explanation = q.get("explanation", "⚠️ Explanation not provided.")

            st.session_state.submitted = True
            st.session_state.last_choice = selected_letter

            if selected_letter == correct_key:
                st.success(f"✅ Correct! {correct_key.upper()}. {correct_text}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Wrong. The correct answer is: {correct_key.upper()}. {correct_text}")
            st.info(f"📘 Explanation: {explanation}")

            if st.button("Next Question"):
                st.session_state.current_q += 1
                st.session_state.submitted = False
                st.session_state.last_choice = ""
                if selected_letter != correct_key:
                    st.session_state.wrong_qs.append(q)
                st.rerun()

    else:
        end_time = time.time()
        total_time = round(end_time - st.session_state.start_time, 2) if st.session_state.start_time else 0
        st.success(f"🎉 Quiz complete, {username}! You scored {st.session_state.score}/{total_questions}")
        st.info(f"⏱ Time Taken: {total_time} seconds")

        st.session_state.leaderboard.append({
            "name": username,
            "score": st.session_state.score,
            "time": total_time
        })

        if st.session_state.wrong_qs:
            st.markdown("### ❌ Review Your Wrong Answers")
            for idx, wrong_q in enumerate(st.session_state.wrong_qs, 1):
                correct_key = wrong_q.get("correct", "").strip().lower()
                correct_text = wrong_q.get(correct_key, "⚠️ Missing option text")
                explanation = wrong_q.get("explanation", "⚠️ Explanation not provided.")
                st.markdown(f"**Q{idx}: {wrong_q.get('question', '⚠️ Question missing')}**")
                st.markdown(f"✅ **Correct Answer:** {correct_key.upper()}. {correct_text}")
                st.markdown(f"📘 **Explanation:** {explanation}")
                st.markdown("---")

        if st.button("🔁 Retry Wrong Questions"):
            st.session_state.quiz_questions = st.session_state.wrong_qs
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.wrong_qs = []
            st.session_state.start_time = time.time()
            st.session_state.submitted = False
            st.rerun()

        if st.button("🔄 Restart Full Quiz"):
            for key in ["current_q", "score", "wrong_qs", "quiz_started", "start_time", "quiz_questions", "submitted", "last_choice"]:
                st.session_state.pop(key, None)
            st.rerun()

# Show leaderboard
if st.session_state.leaderboard:
    st.markdown("## 🏆 Leaderboard")
    sorted_board = sorted(st.session_state.leaderboard, key=lambda x: (-x["score"], x["time"]))
    for i, entry in enumerate(sorted_board, 1):
        st.markdown(f"**{i}. {entry['name']}** — Score: {entry['score']} | Time: {entry['time']}s")
