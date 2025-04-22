#D:\AI interviewer_31-03\AI interviewer\AI interviewer\survey_app_modes\mode1.py
import streamlit as st, os, io, wave
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from openai_functions import transcribe_audio
from db_utils import save_survey_results
from question import QUESTIONS
from custom_css import CUSTOM_CSS
from common_services import get_audio_duration, video_preview
load_dotenv()
# st.markdown(CUSTOM_CSS, unsafe_allow_html=True)



def display_mode_header() -> None:
    st.markdown(
        "<h1 style='text-align:center;'>AI‑Driven Mock Interview</h1>",
        unsafe_allow_html=True,
    )
    st.markdown("<h4 style='text-align:center;'>Mode 1 -Edit Once</h4>",
                unsafe_allow_html=True)

# ----- Page 1: registration --------------------------------------------------
# RFC‑5322–inspired pattern (covers all practical addresses)
import re
# EMAIL_RE = re.compile(
#     r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
#     r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*$"
# )

# General RFC-5322–inspired pattern
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@umbc\.edu$"
)


def registration_page() -> None:
    display_mode_header()
    
    st.warning("Make sure to use your correct email. It will be verified for the payment.")
    st.markdown("<p style='text-align: center;'>Please enter your information to begin</p>", unsafe_allow_html=True)

    # Box to hold any validation message so it stays in the same spot.
    feedback = st.empty()

    with st.form("reg", clear_on_submit=False):
        name  = st.text_input("Name")
        email = st.text_input("Email")

        submitted = st.form_submit_button("Start Interview")

        if submitted:
            if not name.strip():
                feedback.error("Please enter your name.")
            elif not EMAIL_RE.fullmatch(email.strip().lower()):
                feedback.error("Please enter a **valid UMBC email address** "
                               "(must end in @umbc.edu).")
            else:
                st.session_state.user    = {"name": name.strip(),
                                            "email": email.lower()}
                st.session_state.page    = "quiz"
                st.session_state.answers = {}
                st.rerun()
# ----- Page 2: interview ------------------------------------------------------
def interview_page() -> None:
    i = st.session_state.q
    question = QUESTIONS[i]

    display_mode_header()
    st.markdown(f"<div style='font-size:26px'>Question {i+1}/{len(QUESTIONS)}</div>", unsafe_allow_html=True)
    st.markdown(f"### {question}")
    # ── NEW ► optional live camera preview ───────────────────────────────────
    video_preview()     # ← one‑liner; place it wherever you like

    # audio_value = st.audio_input("Record a voice message")

    # if audio_value:
    #      st.audio(audio_value)

    # ---- Record once ---------------------------------------------------------
    if f"audio_{i}" not in st.session_state:
        audio_key = f"audio_input_{i}"
        audio = st.audio_input("Record your answer", key=audio_key)


        if audio:
            #st.audio(audio)  #hiding this because st.audio_input already gives the previeew
            audio_bytes = audio.getvalue()
            dur = get_audio_duration(audio_bytes)
            
            if 30 <= dur <= 180:
                #if st.button("📝 Transcribe", key=f"tr_{i}"): #hiding this as i want to automatically transcribe once user stops recording
                    with st.spinner("Transcribing your response..."):
                        txt = transcribe_audio(audio_bytes)
                    st.session_state[f"audio_{i}"]   = audio
                    st.session_state[f"text_{i}"]    = txt
                    st.session_state[f"edited_{i}"]  = False
                    st.rerun()
            else:
                st.error(f"You recorded **{int(dur)} s**. Must be in between 30 seconds to 3 minutes. Record you answer again by clicking 🎙️ (mic symbol) on the recorder above")

    # ---- Show / edit transcript ---------------------------------------------
    if f"text_{i}" in st.session_state:
        txt_key = f"text_{i}"
        edited  = st.session_state[f"edited_{i}"]
        if not edited:
            if st.button("✏️ Edit Transcript", key=f"editbtn_{i}"):
                st.session_state[f"edit_{i}"] = True
                st.rerun()

        if st.session_state.get(f"edit_{i}", False) and not edited:
            new_txt = st.text_area("Edit once:", st.session_state[txt_key], key=f"ta_{i}")
            if st.button("Save Edited Transcript", key=f"saveedt_{i}"):
                st.session_state[txt_key]   = new_txt
                st.session_state[f"edited_{i}"] = True
                st.session_state.pop(f"edit_{i}")
                st.success("Saved.")
                st.rerun()
        else:
            st.text_area("Transcript", st.session_state[txt_key], disabled=True)

    # ---- Navigation ----------------------------------------------------------
    if f"text_{i}" in st.session_state:
        if i < len(QUESTIONS)-1:
            if st.button("Next ➜", key=f"next_{i}"):
                st.session_state.answers[i] = st.session_state[f"text_{i}"]
                st.session_state.q += 1
                st.rerun()
        else:
            if st.button("Submit Response"):
                st.session_state.answers[i] = st.session_state[f"text_{i}"]
                st.session_state.page = "summary"
                st.rerun()

# ----- Page 3: summary --------------------------------------------------------
def summary_page() -> None:
    st.success("Thanks! Saving your responses …")
    st.success("Go to this link below (Google Forms) to complete the survey")
    st.markdown("https://docs.google.com/forms/d/e/1FAIpQLScnct_vlTzO-tK-5tVERsQ1igxxHIXuP0IEDP2KKzI9EV1p8w/viewform")
    save_survey_results(
        user_info   = st.session_state.user,
        set_number  = 1,
        questions   = QUESTIONS,
        answers     = st.session_state.answers,
        feedback_data = {},
        collection_name = "survey_app_1",
    )
    st.balloons()

# ----- Public entry for this module ------------------------------------------
def render() -> None:
    # init session vars once
    if "page" not in st.session_state: st.session_state.page = "reg"
    if "q"    not in st.session_state: st.session_state.q    = 0

    if st.session_state.page == "reg":
        registration_page()
    elif st.session_state.page == "quiz":
        interview_page()
    else:
        summary_page()
