# AI Unified Feedback Survey App

import streamlit as st
import os
import wave
import io
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from db_utils import save_survey_results
from question import QUESTIONS
from openai_functions import transcribe_audio, get_ai_feedback, motivationalFeedbackGen, informationalFeedbackGen, summarizeFeedback, analyze_transcript_feedback_3
from custom_css import CUSTOM_CSS

load_dotenv()

st.set_page_config(page_title="AI Feedback Survey", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Setup
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'feedback_summaries' not in st.session_state: st.session_state.feedback_summaries = {}
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "email": ""}
if 'page' not in st.session_state: st.session_state.page = "registration"
if 'recorded_audio' not in st.session_state: st.session_state.recorded_audio = None
if 'feedback_type' not in st.session_state: st.session_state.feedback_type = ""

# Registration Page

def show_registration_page():
    st.markdown("<h1 style='text-align: center;'>AI Driven Mock Interview</h1>", unsafe_allow_html=True)
    st.warning("Make sure to use your correct email. It will be verified for the payment.")
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1: name = st.text_input("Name")
        with col2: email = st.text_input("Email")
        submit_button = st.form_submit_button("Start Interview")
        if submit_button:
            if not name or not email:
                st.error("Please provide both name and email to continue.")
            elif "@" not in email or "." not in email:
                st.error("Please provide a valid email address.")
            else:
                st.session_state.user_info = {"name": name, "email": email}
                st.session_state.page = "interview"
                st.rerun()

# Audio Duration Helper

def get_audio_duration(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            return frames / float(rate)
    except Exception:
        return 0

# Interview Page

def show_interview_page():
    current_q_index = st.session_state.current_question_index
    st.markdown(f"<h1>Question {current_q_index + 1} of {len(QUESTIONS)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 18px; font-weight: bold;'>{QUESTIONS[current_q_index]}</p>", unsafe_allow_html=True)

    #st.markdown("### Video Preview")
    st.markdown("""
        <div style='width: 200px; height: 150px; background-color: #000; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white;'>
            Video Preview Only - No Recording
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
                    st.success("Transcription complete.")
                    st.markdown("### Transcript (Read-Only)")
                    st.text_area("", value=text, disabled=True)
                    # summary = get_ai_feedback(QUESTIONS[current_q_index], text)
                    summary = ""
                    if st.session_state.feedback_type == "Feedback1":
                        summary=motivationalFeedbackGen(text)
                    elif st.session_state.feedback_type == "Feedback2":
                        summary=informationalFeedbackGen(QUESTIONS[current_q_index], text)
                    elif st.session_state.feedback_type == "Feedback3":
                        summary=analyze_transcript_feedback_3(QUESTIONS[current_q_index], text)
                    else:
                        summary="You are not on a valid feedback count"                      
                    st.session_state.feedback_summaries[current_q_index] = summary
                    st.success("Summary generated.")
                    st.markdown(f"**Summary for Question {current_q_index + 1}:**")
                    st.markdown(f"*{summary}*")
                except Exception as e:
                    st.error(f"Transcription/feedback failed: {e}")

    if current_q_index in st.session_state.feedback_summaries:
        if current_q_index < len(QUESTIONS) - 1:
            if st.button("Next Question ➡️"):
                st.session_state.current_question_index += 1
                st.session_state.recorded_audio = None
                st.rerun()
        else:
            if st.button("Submit Survey"):
                st.session_state.page = "summary"
                st.rerun()

# Summary Page

def show_summary_page():
    st.markdown("<h1>Thank You for Taking the Feedback Survey!</h1>", unsafe_allow_html=True)
    with st.spinner("Saving your response..."):
        success = save_survey_results(
            user_info=st.session_state.user_info,
            set_number=1,
            questions=QUESTIONS,
            answers=st.session_state.answers,
            feedback_data={i: {"feedback": summary} for i, summary in st.session_state.feedback_summaries.items()},
            collection_name=st.session_state.feedback_type
        )
        if success:
            st.success("Your responses and summaries have been saved successfully!")
        else:
            st.error("Oops! Something went wrong while saving.")

    st.markdown("### Combined Summary")
    combined_feedback_text=""
    for i, summary in st.session_state.feedback_summaries.items():
        #st.markdown(f"**Q{i+1}:** *{summary}*")
        combined_feedback_text+=f"**Q{i+1}:** *{summary}* \n"
    st.markdown(f"*{summarizeFeedback(combined_feedback_text)}*")

    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Entry Point

def main():
    query_params = st.query_params
    for tag in ["feedback1", "feedback2", "feedback3"]:
        if tag in query_params:
            st.session_state.feedback_type = tag.capitalize()
            print(st.session_state.feedback_type)
            break
    else:
        st.error("Missing URL parameter. Use ?feedback1, ?feedback2, or ?feedback3.")
        st.stop()

    if st.session_state.page == "registration":
        show_registration_page()
    elif st.session_state.page == "interview":
        show_interview_page()
    elif st.session_state.page == "summary":
        show_summary_page()

if __name__ == "__main__":
    main()
