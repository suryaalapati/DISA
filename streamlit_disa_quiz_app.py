
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

# UI: Get username and number of questions before starting
username = st.text_input("Enter your name to appear on the leaderboard:")
num_qs = st.slider("🧠 How many questions do you want?", 1, len(questions), 5)
start_button = st.button("Start Quiz")

# Safe init for session state
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "wrong_qs" not in st.session_state:
    st.session_state.wrong_qs = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_choice" not in st.session_state:
    st.session_state.last_choice = ""

# Start quiz
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
        st.markdown(f"### **Q{current_index + 1}/{total_questions}: {q['question']}**")

        options_dict = {
            "A": q.get("a", "Option A missing"),
            "B": q.get("b", "Option B missing"),
            "C": q.get("c", "Option C missing"),
            "D": q.get("d", "Option D missing")
        }

        display_options = [f"{k}. {v}" for k, v in options_dict.items()]
        selected = st.radio("Choose an option:", display_options, index=None, key=f"q{current_index}")

        if st.button("Submit Answer") or st.session_state.submitted:
            correct_option = q.get("correct", "").upper()
            correct_text = options_dict.get(correct_option, "Unknown")
            explanation = q.get("explanation", "No explanation provided.")
            selected_letter = selected.split(".")[0].strip().upper() if selected else ""

            st.session_state.submitted = True
            st.session_state.last_choice = selected_letter

            if selected_letter == correct_option:
                st.success(f"✅ Correct! {correct_option}. {correct_text}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Wrong. The correct answer is: {correct_option}. {correct_text}")
            st.info(f"📘 Explanation: {explanation}")

            if st.button("Next Question"):
                st.session_state.current_q += 1
                st.session_state.submitted = False
                st.session_state.last_choice = ""
                if selected_letter != correct_option:
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
                correct_option = wrong_q.get("correct", "").upper()
                correct_text = wrong_q.get(correct_option.lower(), "")
                explanation = wrong_q.get("explanation", "No explanation provided.")
                st.markdown(f"**Q{idx}: {wrong_q['question']}**")
                st.markdown(f"✅ **Correct Answer:** {correct_option}. {correct_text}")
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
