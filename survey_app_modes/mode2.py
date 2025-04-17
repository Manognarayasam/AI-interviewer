# mode2.py  – Re‑record Only (one extra attempt)  ———————————————
import streamlit as st, io, wave
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from openai_functions import transcribe_audio
from db_utils import save_survey_results
from question import QUESTIONS
from custom_css import CUSTOM_CSS
from common_services import get_audio_duration

load_dotenv()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)



def header() -> None:
    st.markdown("<h4 style='text-align:center;'>Mode 2 – Re‑record Once</h4>",
                unsafe_allow_html=True)


# ───── Registration page ──────────────────────────────────────────────────────
# RFC‑5322–inspired pattern (covers all practical addresses)
import re
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*$"
)

def registration_page() -> None:
    header()
    st.markdown(
        "<h1 style='text-align:center;'>AI‑Driven Mock Interview</h1>",
        unsafe_allow_html=True,
    )
    st.warning("Make sure to use your correct email. It will be verified for the payment.")
    st.markdown("<p style='text-align: center;'>Please enter your information to begin</p>", unsafe_allow_html=True)

    # Box to hold any validation message so it stays in the same spot.
    feedback = st.empty()

    with st.form("reg", clear_on_submit=False):
        name  = st.text_input("Name")
        email = st.text_input("Email")

        submitted = st.form_submit_button("Start Interview")

        if submitted:
            # ---------- Validation ----------
            if not name.strip():
                feedback.error("Please enter your name.")
            elif not EMAIL_RE.fullmatch(email):
                feedback.error("Please enter a **valid e‑mail address** "
                               "(e.g. john.doe@example.com).")
            else:
                # ---------- Success path ----------
                st.session_state.user    = {"name": name.strip(),
                                            "email": email.lower()}
                st.session_state.page    = "quiz"
                st.session_state.answers = {}
                st.rerun()


# ───── Interview page ─────────────────────────────────────────────────────────
# ───── Interview page — Mode 2 (Re‑record only once) ─────────────────────────
def interview() -> None:
    i = st.session_state.q                        # current question index
    question = QUESTIONS[i]

    st.markdown(f"### Question {i+1}/{len(QUESTIONS)}")
    st.markdown(f"<div style='font-size:26px'>{question}</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. Record → Transcribe (first pass or after one allowed re‑record)
    # -------------------------------------------------------------------------
    if f"audio_{i}" not in st.session_state:
        audio = mic_recorder("🟢🎤 Start Recording", "🔴 Recording…",
                             use_container_width=True, key=f"rec_{i}")
        if audio:
            st.audio(audio["bytes"])
            dur = get_audio_duration(audio["bytes"])
            st.info(f"You recorded **{int(dur)} s**")
            if 30 <= dur <= 120:
                if st.button("📝 Transcribe", key=f"tr_{i}"):
                    txt = transcribe_audio(audio["bytes"])
                    st.session_state[f"audio_{i}"] = audio
                    st.session_state[f"text_{i}"]  = txt
                    # create the once‑only flag the FIRST time we transcribe
                    st.session_state.setdefault(f"rer_{i}", False)
                    st.rerun()
            else:
                st.error("Audio must be 30 – 120 s")

    # -------------------------------------------------------------------------
    # 2. Show transcript (read‑only) and optionally ONE re‑record button
    # -------------------------------------------------------------------------
    if f"text_{i}" in st.session_state:
        st.text_area("Transcript", st.session_state[f"text_{i}"], disabled=True)

        # offer re‑record only if it hasn’t been used yet
        if not st.session_state[f"rer_{i}"]:
            st.warning("Re-record option is available only once per question")
            if st.button("🔁 Re‑record Audio", key=f"rerbtn_{i}"):
                # clear previous data and lock out further re‑records
                st.session_state.pop(f"audio_{i}")
                st.session_state.pop(f"text_{i}")
                st.session_state[f"rer_{i}"] = True
                st.rerun()

    # -------------------------------------------------------------------------
    # 3. Navigation (enabled only when we have a transcript)
    # -------------------------------------------------------------------------
    if f"text_{i}" in st.session_state:
        if i < len(QUESTIONS) - 1:
            if st.button("Next ➜", key=f"nxt_{i}"):
                st.session_state.answers[i] = st.session_state[f"text_{i}"]
                st.session_state.q += 1
                st.rerun()
        else:
            if st.button("Submit"):
                st.session_state.answers[i] = st.session_state[f"text_{i}"]
                st.session_state.page = "summary"
                st.rerun()


# ───── Summary page ───────────────────────────────────────────────────────────
def summary() -> None:
    st.success("Thanks! Saving your responses …")
    save_survey_results(
        user_info       = st.session_state.user,
        set_number      = 2,
        questions       = QUESTIONS,
        answers         = st.session_state.answers,
        feedback_data   = {},
        collection_name = "survey_app_2",
    )
    st.balloons()


# ───── Public entry point ─────────────────────────────────────────────────────
def render() -> None:
    if "page" not in st.session_state: st.session_state.page = "reg"
    if "q"    not in st.session_state: st.session_state.q    = 0

    if st.session_state.page == "reg":
        registration_page()
    elif st.session_state.page == "quiz":
        interview()
    else:
        summary()
