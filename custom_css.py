#custom_css.py
CUSTOM_CSS="""
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    [data-testid="stCameraInputWebcamStyledBox"] div {
        width: 260px;
        height: 220px;
    }

    /* 🔧 Resize camera preview cleanly */
    [data-testid="stCameraInput"] video {
        width: 240px !important;
        height: 200px !important;
        object-fit: cover !important;
        border-radius: 8px;
        margin: auto;
    }
       /* 🔧 Resize outer container to match */
    [data-testid="stCameraInput"] > div {
        width: 260px !important;
        margin: auto;
        display: flex !important;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* Make the mic recorder button green by default */
    button[data-testid="baseButton"] {
        background-color: green !important;
        color: white !important;
        font-size: 18px !important;
        border-radius: 8px !important;
        transition: background-color 0.3s ease;
    }

    /* When recording is active, mic recorder button becomes red */
    button[data-testid="baseButton"].stRecording {
        background-color: red !important;
        color: white !important;
    }
   
</style>
"""