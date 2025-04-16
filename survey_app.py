# AI Feedback Survey App

import streamlit as st
import os
import wave
import io
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from db_utils import save_survey_results
from question import QUESTIONS
from openai_functions import transcribe_audio
from custom_css import CUSTOM_CSS

load_dotenv()

st.set_page_config(page_title="AI Driven Mock Interview", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Setup
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'transcribed_text' not in st.session_state: st.session_state.transcribed_text = ""
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "email": ""}
if 'page' not in st.session_state: st.session_state.page = "registration"
if 'recorded_audio' not in st.session_state: st.session_state.recorded_audio = None
if 'show_video_preview' not in st.session_state: st.session_state.show_video_preview = True
if 'rerecorded' not in st.session_state: st.session_state.rerecorded = {}
if 'edit_transcript' not in st.session_state: st.session_state.edit_transcript = False

# Determine mode (edit, re-record, both)
def get_app_config():
    mode = int(st.session_state.get("mode", 1))
    return {
        "can_edit": mode == 1 or mode == 3,
        "can_rerecord": mode == 2 or mode == 3
    }

def display_mode_header():
    mode = st.session_state.get("mode", 1)
    label = {1: "Edit Only", 2: "Re-record Only", 3: "Edit & Re-record"}[mode]
    st.markdown(f"<h4 style='text-align:center;'>Mode: {label}</h4>", unsafe_allow_html=True)

def show_registration_page():
    display_mode_header()
    st.markdown("<h1 style='text-align: center;'>AI Driven Mock Interview</h1>", unsafe_allow_html=True)
    st.warning("Make sure to use your correct email. It will be verified for the payment.")
    st.markdown("<p style='text-align: center;'>Please enter your information to begin</p>", unsafe_allow_html=True)

    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
        with col2:
            email = st.text_input("Email")

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

def get_audio_duration(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            return frames / float(rate)
    except Exception:
        return 0

def show_interview_page():
    config = get_app_config()
    display_mode_header()

    current_q_index = st.session_state.current_question_index
    st.markdown(f"<h4>Question {current_q_index + 1} of {len(QUESTIONS)}</h4>", unsafe_allow_html=True)
    st.markdown(
    f"<div style='font-size:26px; font-weight:500;'>{QUESTIONS[current_q_index]}</div>",
    unsafe_allow_html=True
)

    #st.markdown(f"<h1>Question {current_q_index + 1} of {len(QUESTIONS)}</h1>", unsafe_allow_html=True)
    #st.write(QUESTIONS[current_q_index])

    #st.markdown("### Video Preview")
    col = st.columns([3, 2, 3])[1]
    with col:
        st.markdown(f"""
            <div style='
                width: 200px;
                height: 150px;
                background-color: #eee;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 10px;
                font-weight: bold;
            '>
                {st.session_state.user_info.get("name", "User")}'s Preview
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### Record Your Answer (Audio Only)")
    audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key=f"audio_{current_q_index}")

    if audio:
        st.session_state.recorded_audio = audio
        st.audio(audio['bytes'])
        duration = get_audio_duration(audio['bytes'])
        st.session_state[f"audio_duration_{current_q_index}"] = duration

        if st.button("📝 Transcribe", key=f"transcribe_{current_q_index}"):
            with st.spinner("Transcribing..."):
                try:
                    text = transcribe_audio(audio['bytes'])
                    st.session_state.transcribed_text = text
                    st.session_state.answers[current_q_index] = text
                    st.success("Transcription saved.")
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    if st.session_state.transcribed_text:
        st.markdown("### Transcribed Text")
        if config["can_edit"] and st.session_state.get("edit_transcript"):
            edited_text = st.text_area("Edit Transcript", value=st.session_state.transcribed_text, height=150)
            if st.button("Save Edited Transcript"):
                st.session_state.transcribed_text = edited_text
                st.session_state.answers[current_q_index] = edited_text
                st.session_state.edit_transcript = False
                st.success("Transcript updated.")
        else:
            st.text_area("Transcript", value=st.session_state.transcribed_text, height=150, disabled=True)

        if config["can_edit"] and not st.session_state.get("edit_transcript"):
            if st.button("✏️ Edit Transcript"):
                st.session_state.edit_transcript = True

        if config["can_rerecord"] and not st.session_state.rerecorded.get(current_q_index, False):
            if st.button("🔁 Re-record Audio"):
                st.session_state.transcribed_text = ""
                st.session_state.recorded_audio = None
                st.session_state.rerecorded[current_q_index] = True
                st.success("You may now record again.")
                st.rerun()

    if current_q_index < len(QUESTIONS) - 1:
        if st.button("Save and Go to Next Question"):
            st.session_state.answers[current_q_index] = st.session_state.transcribed_text
            st.session_state.current_question_index += 1
            st.session_state.transcribed_text = ""
            st.session_state.recorded_audio = None
            st.session_state.edit_transcript = False
            st.rerun()
    else:
        if st.button("Submit"):
            st.session_state.answers[current_q_index] = st.session_state.transcribed_text
            st.session_state.page = "summary"
            st.success("Response recorded.")
            st.rerun()

def show_summary_page():
    st.markdown("<h1>Thank You for Taking the Survey!</h1>", unsafe_allow_html=True)
    with st.spinner("Saving your response..."):
        success = save_survey_results(
            user_info=st.session_state.user_info,
            set_number=st.session_state.get("mode", 1),
            questions=QUESTIONS,
            answers=st.session_state.answers,
            feedback_data={},
            collection_name = f"survey_app_{st.session_state.mode}"
        )
        if success:
            st.success("Your response has been saved successfully!")
        else:
            st.error("Oops! Something went wrong while saving.")
    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    query_params = st.query_params
    if 'mode' in query_params:
        try:
            mode = int(query_params['mode'][0])
            if mode in [1, 2, 3]:
                st.session_state.mode = mode
            else:
                st.error("Invalid mode. Use ?mode=1 (Edit), ?mode=2 (Re-record), or ?mode=3 (Both).")
                st.stop()
        except ValueError:
            st.error("Invalid mode. Use an integer: 1, 2, or 3.")
            st.stop()
    else:
        st.error("Missing 'mode' parameter. Add ?mode=1, 2, or 3 in the URL.")
        st.stop()

    if st.session_state.page == "registration":
        show_registration_page()
    elif st.session_state.page == "interview":
        show_interview_page()
    elif st.session_state.page == "summary":
        show_summary_page()

if __name__ == "__main__":
    main()
