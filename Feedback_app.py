# AI Unified Feedback Survey App

import streamlit as st
import os
import wave
import io
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from db_utils import save_survey_results
from question import FEEDBACK_QUESTIONS as QUESTIONS
from openai_functions import transcribe_audio, get_ai_feedback, motivationalFeedbackGen, informationalFeedbackGen, summarizeFeedback, analyze_transcript_feedback_3
from custom_css import CUSTOM_CSS
from common_services import get_audio_duration, video_preview


load_dotenv()

st.set_page_config(page_title="Feedback Study", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Setup
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'feedback_summaries' not in st.session_state: st.session_state.feedback_summaries = {}
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "email": ""}
if 'page' not in st.session_state: st.session_state.page = "registration"
if 'recorded_audio' not in st.session_state: st.session_state.recorded_audio = None
if 'feedback_type' not in st.session_state: st.session_state.feedback_type = ""

import re

# Only allow UMBC emails
UMBC_EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@umbc\.edu$")

def show_registration_page():
    st.markdown("<h1 style='text-align: center;'>AI Driven Mock Interview</h1>", unsafe_allow_html=True)
    st.warning("Make sure to use your correct UMBC email. It will be verified for the payment.")
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
        with col2:
            email = st.text_input("Email")
        
        submit_button = st.form_submit_button("Start Interview")
        
        if submit_button:
            if not name.strip() or not email.strip():
                st.error("Please provide both name and email to continue.")
            elif not UMBC_EMAIL_RE.fullmatch(email.strip().lower()):
                st.error("Please provide a valid UMBC email address (must end in @umbc.edu).")
            else:
                st.session_state.user_info = {
                    "name": name.strip(),
                    "email": email.strip().lower()
                }
                st.session_state.page = "interview"
                st.rerun()

# Interview Page

def show_interview_page():
    current_q_index = st.session_state.current_question_index
    st.markdown(f"<p> Question {current_q_index + 1} of {len(QUESTIONS)}</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-weight: bold;'>{QUESTIONS[current_q_index]}</h2>", unsafe_allow_html=True)

    video_preview()
   

    st.markdown("### Record Your Answer (Audio Only)")
    #audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key=f"audio_{current_q_index}")

        # --- Record answer -------------------------------------------------------
    # audio = mic_recorder(start_prompt="🎙️ Start Recording",
    #                      stop_prompt="⏹️ Stop Recording",
    #                      key=f"audio_{current_q_index}")
    
    # if f"audio_{i}" not in st.session_state:
    audio_key = f"audio_{current_q_index}"
    audio = st.audio_input("Record your answer", key=audio_key)

    if audio:                                              # user stopped recording
        st.session_state.recorded_audio = audio
        audio_bytes = audio.getvalue()
        #st.audio(audio_bytes)

        # 👇 NEW —–––––––––––––––––––––––––––––––––––––––––––––––––––
        dur_sec = get_audio_duration(audio_bytes)
        st.info(f"You recorded **{int(dur_sec)} s**")

        if 3 <= dur_sec <= 180:                           # ⟵ gate transcription
            if st.button("📝 Transcribe", key=f"tr_{current_q_index}"):
                with st.spinner("Transcribing…"):
                    try:
                        text = transcribe_audio(audio_bytes)
                        st.session_state.answers[current_q_index] = text
                        st.success("Transcription complete.")

                        st.markdown("### Transcript (read‑only)")
                        st.text_area("", value=text, disabled=True)

                        # ­‑‑‑ generate feedback exactly as before ­‑‑‑
                        summary = ""
                        if st.session_state.feedback_type == "Motivational Feedback":
                            summary = motivationalFeedbackGen(text)
                        elif st.session_state.feedback_type == "Informational Feedback":
                            summary = informationalFeedbackGen(
                                QUESTIONS[current_q_index], text)
                        elif st.session_state.feedback_type == "Motivational and Informational Feedback":
                            summary = analyze_transcript_feedback_3(
                                QUESTIONS[current_q_index], text)
                        else:
                            summary = "You are not on a valid feedback count"

                        st.session_state.feedback_summaries[current_q_index] = summary
                        st.success("Summary generated.")
                        st.markdown(f"**Feedback for Question "
                                    f"{current_q_index + 1}:**")
                        st.markdown(f"*{summary}*")
                    except Exception as e:
                        st.error(f"Transcription/feedback failed: {e}")
        else:
            st.error("Recording must be **between 30 s and 3 min**. "
                     "Please re‑record.")

    if current_q_index in st.session_state.feedback_summaries:
        if current_q_index < len(QUESTIONS) - 1:
            if st.button("Next Question ➡️"):
                st.session_state.current_question_index += 1
                st.session_state.recorded_audio = None
                st.rerun()
        else:
            if st.button("Submit Response"):
                st.session_state.page = "summary"
                st.rerun()

# Summary Page

def show_summary_page():
    st.markdown("<h1>Thank You for completing the study!</h1>", unsafe_allow_html=True)
    with st.spinner("Go to the next link below to take next study"):
        success = save_survey_results(
            user_info=st.session_state.user_info,
            set_number=1,
            questions=QUESTIONS,
            answers=st.session_state.answers,
            feedback_data={i: {"feedback": summary} for i, summary in st.session_state.feedback_summaries.items()},
            collection_name=st.session_state.feedback_type
        )
        if success:
            st.success("Your responses have been saved successfully!")
        else:
            st.error("Oops! Something went wrong while saving.")

    st.markdown("### Feedback")
    combined_feedback_text=""
    for i, summary in st.session_state.feedback_summaries.items():
        #st.markdown(f"**Q{i+1}:** *{summary}*")
        combined_feedback_text+=f"**Q{i+1}:** *{summary}* \n"
    #st.markdown(f"*{summarizeFeedback(combined_feedback_text)}*")
    st.markdown(f"*{summarizeFeedback(combined_feedback_text, st.session_state.feedback_type)}*")



    st.markdown("---")
    st.markdown("### Continue to the Post-Task Survey")

    if st.session_state.feedback_type == "Feedback1":
        st.link_button("📘 Provide Your Feedback", "https://forms.gle/9e94ZhVyjDrVQbUb6", type="primary")
    elif st.session_state.feedback_type == "Feedback2":
        st.link_button("💡 Provide Your Feedback", "https://forms.gle/wbFjeCHfvy6idVmf6", type="primary")
    elif st.session_state.feedback_type == "Feedback3":
        st.link_button("🔀 Provide Your Feedback", "https://forms.gle/zUkj3gnX6NnUC1RQ8", type="primary")



    # if st.button("Start Over"):
    #     for key in list(st.session_state.keys()):
    #         del st.session_state[key]
    #     st.rerun()

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

