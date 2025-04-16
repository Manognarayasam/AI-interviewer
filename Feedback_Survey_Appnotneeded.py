# AI Feedback Survey App

import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from db_utils import save_survey_results
from question import QUESTIONS
from openai_functions import transcribe_audio, get_ai_feedback
from custom_css import CUSTOM_CSS

# Load environment and CSS
load_dotenv()
st.set_page_config(page_title="AI Feedback Survey", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Setup
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'transcribed_texts' not in st.session_state: st.session_state.transcribed_texts = {}
if 'feedback_data' not in st.session_state: st.session_state.feedback_data = {}
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "email": ""}
if 'page' not in st.session_state: st.session_state.page = "registration"
if 'show_video_preview' not in st.session_state: st.session_state.show_video_preview = True

# Registration Page
def show_registration():
    st.markdown("<h1 style='text-align: center;'>AI Feedback Survey</h1>", unsafe_allow_html=True)
    with st.form("user_info_form"):
        col1, col2 = st.columns(2)
        with col1: name = st.text_input("Name")
        with col2: email = st.text_input("Email")
        if st.form_submit_button("Start Survey"):
            if name and email:
                st.session_state.user_info = {"name": name, "email": email}
                st.session_state.page = "interview"
                st.rerun()
            else:
                st.error("Please provide name and email")

# Interview Page
def show_interview_page():
    current_q_index = st.session_state.current_question_index
    st.markdown(f"<h2>Question {current_q_index + 1} of {len(QUESTIONS)}</h2>", unsafe_allow_html=True)
    st.write(QUESTIONS[current_q_index])

    st.markdown("### Video Preview")
    st.session_state.show_video_preview = st.checkbox("Show Video Preview", value=st.session_state.show_video_preview)
    col = st.columns([3, 2, 3])[1]
    with col:
        if st.session_state.show_video_preview:
            st.camera_input(label="Video preview", key="mimic_camera")
        else:
            st.markdown(f"""
                <div style='width: 200px; height: 150px; background-color: black; color: white;
                            display: flex; align-items: center; justify-content: center;
                            border-radius: 10px; font-weight: bold;'>
                    {st.session_state.user_info.get("name", "User")}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("### Record Your Answer (Audio Only)")
    audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key=f"audio_{current_q_index}")

    if audio:
        st.session_state.recorded_audio = audio
        st.audio(audio['bytes'])
        if st.button("📝 Transcribe", key=f"transcribe_{current_q_index}"):
            with st.spinner("Transcribing..."):
                try:
                    text = transcribe_audio(audio['bytes'])
                    st.session_state.answers[current_q_index] = text
                    st.session_state.transcribed_texts[current_q_index] = text
                    st.rerun()
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    if current_q_index < len(QUESTIONS) - 1:
        if st.button("Next Question ➡️"):
            st.session_state.current_question_index += 1
            st.session_state.transcribed_text = ""
            st.session_state.recorded_audio = None
            st.rerun()
    else:
        if st.button("Finish & Submit"):
            query_params = st.query_params
            mode_param = int(query_params.get("mode", ["3"])[0])
            collection_name = query_params.get("collection", ["user_survey_analysis"])[0]

            feedback_data = {}
            for i in range(len(QUESTIONS)):
                text = st.session_state.transcribed_texts.get(i, "").strip()
                question = QUESTIONS[i]
                if text:
                    feedback = get_ai_feedback(question, text)
                    if mode_param == 1:
                        feedback_data[i] = {"score": feedback.get("score", 0)}
                    elif mode_param == 2:
                        feedback_data[i] = {"feedback": feedback.get("feedback", "")}
                    else:
                        feedback_data[i] = feedback
                else:
                    feedback_data[i] = {
                        "score": 0,
                        "feedback": "No answer provided.",
                        "strengths": [],
                        "areasforimprovement": ["Answer not recorded."]
                    }

            save_survey_results(
                user_info=st.session_state.user_info,
                set_number=mode_param,
                questions=QUESTIONS,
                answers=st.session_state.transcribed_texts,
                feedback_data=feedback_data,
                collection_name="Feedback_Survey_app"
            )

            st.session_state.feedback_result = feedback_data
            st.session_state.page = "summary"
            st.rerun()

# Summary Page
def show_summary():
    st.markdown("<h2>Thank you! Here's your feedback:</h2>", unsafe_allow_html=True)
    feedback_result = st.session_state.feedback_result
    for i, feedback in feedback_result.items():
        st.markdown(f"**Question {i+1}**")
        if "score" in feedback:
            st.markdown(f"- **Score**: {feedback.get('score', 0)}")
        if "feedback" in feedback:
            st.markdown(f"- **Summary**: {feedback.get('feedback', '')}")
        if "strengths" in feedback:
            st.markdown(f"- **Strengths**: {', '.join(feedback['strengths'])}")
        if "areasforimprovement" in feedback:
            st.markdown(f"- **Improvements**: {', '.join(feedback['areasforimprovement'])}")

    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Router
if st.session_state.page == "registration":
    show_registration()
elif st.session_state.page == "interview":
    show_interview_page()
elif st.session_state.page == "summary":
    show_summary()
