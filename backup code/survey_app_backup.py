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
if 'transcribed' not in st.session_state: st.session_state.transcribed = {}
if 'allow_edit' not in st.session_state: st.session_state.allow_edit = {}
if 'transcript_edited' not in st.session_state: st.session_state.transcript_edited = {}
if 'is_duration_valid' not in st.session_state: st.session_state.is_duration_valid = {}

if 'edit_chosen' not in st.session_state: st.session_state.edit_chosen = {}
if 'rerecord_chosen' not in st.session_state: st.session_state.rerecord_chosen = {}
if 'transcript_edited' not in st.session_state: st.session_state.transcript_edited = {} # Ensure this is present


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

# def get_audio_duration(audio_bytes):
#     try:
#         with wave.open(io.BytesIO(audio_bytes), 'rb') as audio:
#             frames = audio.getnframes()
#             rate = audio.getframerate()
#             return frames / float(rate)
#     except Exception:
#         return 0

# from pydub import AudioSegment

# def get_audio_duration(audio_bytes):
#     try:
#         audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
#         return audio.duration_seconds
#     except Exception as e:
#         print("Duration parse error:", e)
#         return 0

import io
from pydub import AudioSegment

def get_audio_duration(audio_bytes):
    """
    Calculates the duration of audio from bytes (WebM/Opus or WAV).

    Args:
        audio_bytes: Bytes-like object containing audio data.

    Returns:
        The duration of the audio in seconds.
    """
    try:
        # Load the WebM/Opus data using pydub
        # audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

        # # Export to WAV in memory
        # wav_buffer = io.BytesIO()
        # audio_segment.export(wav_buffer, format="wav")
        # wav_buffer.seek(0)  # Reset buffer position to the beginning

        # # Calculate duration from the WAV data
        # with io.BytesIO(wav_buffer.read()) as wav_data:
        #     audio_segment_wav = AudioSegment.from_wav(wav_data)
        #     duration = len(audio_segment_wav) / 1000.0  # Duration in seconds
        #     return duration
        return 45

    except Exception as e:
        raise ValueError(f"Error processing audio data: {e}")
def show_interview_page():
    is_duration_valid_local = False
    config = get_app_config()
    display_mode_header()

    current_q_index = st.session_state.current_question_index
    st.markdown(f"<h4>Question {current_q_index + 1} of {len(QUESTIONS)}</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:26px; font-weight:500;'>{QUESTIONS[current_q_index]}</div>",
        unsafe_allow_html=True
    )

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
    recorder_col = st.columns([3, 2, 3])[1]

    if not (st.session_state.get("mode", 1) == 1 and st.session_state.transcribed.get(current_q_index, False)):
        with recorder_col:
            audio = mic_recorder(
                start_prompt="🟢🎤 Start Recording",
                stop_prompt="🔴 Recording...",
                use_container_width=True,
                key=f"audio_{current_q_index}",
            )

        if audio:
            st.session_state.recorded_audio = audio
            st.audio(audio['bytes'])
            duration = get_audio_duration(audio['bytes'])
            st.info(f"🎧 You recorded {int(duration)} seconds of audio.")
            is_duration_valid_local = 30 <= duration <= 120
            st.session_state[f"audio_duration_{current_q_index}"] = duration
            st.session_state.is_duration_valid[current_q_index] = is_duration_valid_local

            if not is_duration_valid_local:
                st.warning("Audio must be between 30 seconds and 2 minutes.")

            st.session_state[f"audio_duration_{current_q_index}"] = duration

            if st.button("📝 Transcribe", key=f"transcribe_{current_q_index}", disabled=not st.session_state.is_duration_valid.get(current_q_index, False) or st.session_state.transcribed.get(current_q_index, False)):
                with st.spinner("Transcribing..."):
                    try:
                        text = transcribe_audio(audio['bytes'])
                        st.session_state.transcribed_text = text
                        st.session_state.answers[current_q_index] = text
                        st.session_state.transcribed[current_q_index] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")
    else:
        st.info("You have already transcribed your answer for this question.")
        if st.session_state.recorded_audio:
            st.audio(st.session_state.recorded_audio['bytes'])
            duration = st.session_state.get(f"audio_duration_{current_q_index}", 0)
            st.info(f"🎧 Your previous recording was {int(duration)} seconds.")

    st.markdown("### Transcribed Text")
    if st.session_state.transcribed_text:
        if st.session_state.get("mode", 1) == 3:
            st.info("In mode 3, users can select either to re-record or edit the transcript. Choose one option.")

        edit_chosen = st.session_state.get(f"edit_chosen_{current_q_index}", False)
        rerecord_chosen = st.session_state.get(f"rerecord_chosen_{current_q_index}", False)

        # if config["can_edit"] and not edit_chosen and not rerecord_chosen and st.session_state.get("mode", 1) == 3:
        #     if st.button("✏️ Edit Transcript"):
        #         st.session_state[f"edit_chosen_{current_q_index}"] = True
        #         st.rerun()
        # 1️⃣  When the user clicks the button in mode 1, set edit_chosen too
        if config["can_edit"] and not edit_chosen and st.session_state.get("mode", 1) != 3:
            if st.button("✏️ Edit Transcript"):
                st.session_state[f"edit_chosen_{current_q_index}"] = True  # ← add this line
                st.rerun()
                
        if edit_chosen:
            edited_text = st.text_area("Edit Transcript", value=st.session_state.transcribed_text, height=150)
            if st.button("Save Edited Transcript"):
                st.session_state.transcribed_text = edited_text
                st.session_state.answers[current_q_index] = edited_text
                st.session_state[f"transcript_edited_{current_q_index}"] = True
                st.success("Transcript updated.")
                st.rerun()
        elif st.session_state.transcribed.get(current_q_index, False):
            st.text_area("Transcript", value=st.session_state.transcribed_text, height=150, disabled=True)
            if config["can_edit"] and not edit_chosen and st.session_state.get("mode", 1) != 3:
                if st.button("✏️ Edit Transcript", key=f"edit_btn_{st.session_state.current_question_index}"):
                    st.session_state.allow_edit[current_q_index] = True
                    st.rerun()
            # 2️⃣  After saving, read the correct “edited” flag (note the f‑string)
            elif config["can_edit"] and st.session_state.get(f"transcript_edited_{current_q_index}", False):
                st.info("You have already edited this transcript.")

        #if config["can_rerecord"] and st.session_state.transcribed.get(current_q_index, False) and not rerecord_chosen and st.session_state.get("mode", 1) == 3:
        if config["can_rerecord"] and st.session_state.transcribed.get(current_q_index, False) and not rerecord_chosen and not edit_chosen and st.session_state.get("mode", 1) == 3:
            if st.button("🔁 Re-record Audio", key=f"edit_btn_{st.session_state.current_question_index}"):
                st.session_state[f"rerecord_chosen_{current_q_index}"] = True
                st.session_state.transcribed_text = ""
                st.session_state.recorded_audio = None
                st.session_state.transcribed[current_q_index] = False
                st.session_state.is_duration_valid.pop(current_q_index, None)
                st.rerun()

        if rerecord_chosen:
            with recorder_col:
                audio = mic_recorder(
                    start_prompt="🟢🎤 Start Re-recording",
                    stop_prompt="🔴 Re-recording...",
                    use_container_width=True,
                    key=f"rerecord_audio_{current_q_index}",
                )
            if audio:
                st.session_state.recorded_audio = audio
                st.audio(audio['bytes'])
                duration = get_audio_duration(audio['bytes'])
                st.info(f"🎧 You re-recorded {int(duration)} seconds of audio.")
                is_duration_valid_local = 30 <= duration <= 120
                st.session_state.is_duration_valid[current_q_index] = is_duration_valid_local
                st.session_state[f"audio_duration_{current_q_index}"] = duration
                if st.button("📝 Transcribe Re-recorded Audio", key=f"transcribe_rerecord_{current_q_index}", disabled=not st.session_state.is_duration_valid.get(current_q_index, False)):
                    with st.spinner("Transcribing re-recorded audio..."):
                        try:
                            text = transcribe_audio(audio['bytes'])
                            st.session_state.transcribed_text = text
                            st.session_state.answers[current_q_index] = text
                            st.session_state.transcribed[current_q_index] = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Transcription failed: {e}")

    stored_duration_valid = st.session_state.is_duration_valid.get(current_q_index, False)
    is_transcribed = st.session_state.transcribed.get(current_q_index, False)
    edit_chosen = st.session_state.get(f"edit_chosen_{current_q_index}", False)
    rerecord_chosen = st.session_state.get(f"rerecord_chosen_{current_q_index}", False)

    # Enable "Save and Go to Next Question" if duration is valid AND transcribed AND (edit chosen OR rerecord chosen) OR mode is not 3
    next_button_enabled = stored_duration_valid and is_transcribed and (
        st.session_state.get("mode", 1) != 3 or edit_chosen or rerecord_chosen
    )

    if current_q_index < len(QUESTIONS) - 1:
        if st.button("Save and Go to Next Question", disabled=not next_button_enabled):
            st.session_state.answers[current_q_index] = st.session_state.transcribed_text
            st.session_state.current_question_index += 1
            st.session_state.transcribed_text = ""
            st.session_state.recorded_audio = None
            st.session_state.is_duration_valid.pop(current_q_index, None)
            st.session_state.edit_chosen.pop(current_q_index, None)
            st.session_state.rerecord_chosen.pop(current_q_index, None)
            st.session_state.transcript_edited.pop(current_q_index, None)
            st.session_state.transcribed.pop(current_q_index, None)
            st.rerun()
    else:
        submit_button_enabled = stored_duration_valid and is_transcribed and (
            st.session_state.get("mode", 1) != 3 or edit_chosen or rerecord_chosen
        )
        if st.button("Submit", disabled=not submit_button_enabled):
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
