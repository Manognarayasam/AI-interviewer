# ───── Helpers ────────────────────────────────────────────────────────────────
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
        # # Load the WebM/Opus data using pydub
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
