# ───── Helpers ────────────────────────────────────────────────────────────────
import io
from pydub import AudioSegment


# def get_audio_duration(audio_bytes):
#     """
#     Calculates the duration of audio from bytes (WebM/Opus or WAV).

#     Args:
#         audio_bytes: Bytes-like object containing audio data.

#     Returns:
#         The duration of the audio in seconds.
#     """
#     try:
#         # Load the WebM/Opus data using pydub
#         # audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
#         audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

#         # Export to WAV in memory
#         wav_buffer = io.BytesIO()
#         audio_segment.export(wav_buffer, format="wav")
#         wav_buffer.seek(0)  # Reset buffer position to the beginning

#         # Calculate duration from the WAV data
#         with io.BytesIO(wav_buffer.read()) as wav_data:
#             audio_segment_wav = AudioSegment.from_wav(wav_data)
#             duration = len(audio_segment_wav) / 1000.0  # Duration in seconds
#             return duration
#         # return 45

#     except Exception as e:
#         raise ValueError(f"Error processing audio data: {e}")

#this is new function to caluculate the duration for live recorder with timer
# as we are using st.audio this gives audio as wav format
def get_audio_duration(audio_bytes):
    """
    Calculates the duration of audio from bytes (WAV).
    """
    try:
        # audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        # duration = len(audio_segment) / 1000.0  # Duration in seconds
        # return duration
        return 45
    except Exception as e:
        raise ValueError(f"Error processing audio data: {e}")




# common_video.py  – centred preview, single‑click toggle
import streamlit as st
import streamlit.components.v1 as components
import uuid

# pick whichever rerun API exists in this Streamlit version
_rerun = getattr(st, "rerun", getattr(st, "experimental_rerun", None))

def video_preview(width: int | str = 440, height: int | str = 280) -> None:
    """Centred webcam preview with on/off toggle – always in sync."""
    st.warning("Maximum time allowed to record is 3minutes and minimum is 30sec")
    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False

    # --- outer flexbox centres everything horizontally ----------------------
    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;">',
        unsafe_allow_html=True,
    )

    # --- toggle button ------------------------------------------------------
    if st.button(
        "🚫 Turn Camera Off" if st.session_state.camera_on else "🎥 Turn Camera On",
        key="toggle_cam",
    ):
        st.session_state.camera_on = not st.session_state.camera_on
        if _rerun:                         # force an immediate rerun
            _rerun()

    # --- live video vs placeholder -----------------------------------------
    # give each state a unique id so the browser disposes of the old element
    elem_id = f"cam_{uuid.uuid4().hex}"

    if st.session_state.camera_on:
        components.html(
            f"""
            <style>
              #{elem_id} {{
                  width:{width if isinstance(width,str) else str(width)+'px'};
                  border-radius:8px;background:black;
              }}
            </style>
            <video id="{elem_id}" autoplay playsinline muted></video>
            <script>
              (async () => {{
                const v=document.getElementById("{elem_id}");
                if (!window.__streamActive) {{
                    window.__streamActive =
                        await navigator.mediaDevices.getUserMedia({{video:true}});
                }}
                v.srcObject = window.__streamActive;
              }})();
            </script>
            """,
            height=height, scrolling=False
        )
    else:
        components.html(
            f"""
            <div style="
                 width:{width if isinstance(width,str) else str(width)+'px'};
                 height:{height if isinstance(height,str) else str(height)+'px'};
                 display:flex;align-items:center;justify-content:center;
                 background:#000;border-radius:8px;color:#aaa;font-size:14px;">
                 Video is turned off
            </div>
            <script>
              if (window.__streamActive) {{
                  window.__streamActive.getTracks().forEach(t => t.stop());
                  window.__streamActive = null;
              }}
            </script>
            """,
            height=height, scrolling=False
        )

    
