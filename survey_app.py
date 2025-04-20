#D:\AI interviewer_31-03\AI interviewer\AI interviewer\survey_app.py
import streamlit as st
st.set_page_config(page_title="AI‑Driven Mock Interview", layout="wide")
from survey_app_modes import mode1, mode2, mode3, page_not_found

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
reduce_top_padding = """
<style>
/* 1️⃣ shrink the container’s own padding‑top */
section.main > div.block-container,
div.stMainBlockContainer.block-container {
    padding-top: 0.25rem !important;   /* ← pick any value or 0 */
}

/* 2️⃣ kill the automatic top margin Streamlit gives the first element */
div.stVerticalBlock > :first-child {        /* Streamlit ≤1.29 */
    margin-top: 0 !important;
}
/* fallback for newer versions that renamed the class */
div[data-testid="stVerticalBlock"] > :first-child {
    margin-top: 0 !important;
}
</style>
"""
st.markdown(reduce_top_padding, unsafe_allow_html=True)


def main() -> None:
    # Pick mode from the query string. Default = 1.
    mode = st.query_params.get("mode", ["4"])[0]
    print(mode)
    if mode == "2":
        mode2.render()
    elif mode == "3":
        mode3.render()
    elif mode == "1":
        mode1.render()
    else:
        page_not_found.render()  

if __name__ == "__main__":
    main()
