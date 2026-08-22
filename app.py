import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from utils.asr import transcribe_audio
from utils.summarizer import generate_meeting_summary


# Load environment variables
load_dotenv()


# Page configuration
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙️",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "meeting_report" not in st.session_state:
    st.session_state.meeting_report = None

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "audio_name" not in st.session_state:
    st.session_state.audio_name = None

if "temp_audio_path" not in st.session_state:
    st.session_state.temp_audio_path = None


# =========================================================
# BACKGROUND
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #eef2ff,
            #f5f3ff,
            #ecfeff
        );
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 15px;
        padding: 10px;
        border: 2px dashed #a5b4fc;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        );
        color: white;
        border: none;
        border-radius: 12px;
        height: 50px;
        font-weight: bold;
    }

    .stDownloadButton > button {
        width: 100%;
        border-radius: 12px;
        height: 48px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================

st.title("🎙️ Meeting Summarizer")

st.write(
    "Transform meeting recordings into structured "
    "and actionable insights."
)


# =========================================================
# API KEY
# =========================================================

if not os.getenv("GROQ_API_KEY"):

    st.error(
        "Groq API key is not configured. "
        "Please check your .env file."
    )

    st.stop()


# =========================================================
# UPLOAD
# =========================================================

st.header("📤 Upload Meeting Recording")

st.info(
    "🎧 Select a meeting audio file. "
    "The system will convert the recording into text "
    "and generate a structured meeting report."
)


uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=[
        "mp3",
        "wav",
        "m4a",
        "mpeg",
        "mpga",
        "webm"
    ]
)


# =========================================================
# FILE HANDLING
# =========================================================

if uploaded_file is not None:

    current_file = (
        uploaded_file.name,
        uploaded_file.size
    )


    # -----------------------------------------------------
    # NEW FILE SELECTED
    # -----------------------------------------------------

    if st.session_state.processed_file != current_file:

        st.session_state.transcript = None

        st.session_state.meeting_report = None

        st.session_state.processed_file = current_file

        st.session_state.audio_data = (
            uploaded_file.getvalue()
        )

        st.session_state.audio_name = (
            uploaded_file.name
        )


# =========================================================
# DISPLAY AUDIO
# =========================================================

if st.session_state.audio_data is not None:

    st.audio(
        st.session_state.audio_data
    )

    st.success(
        f"File selected: "
        f"{st.session_state.audio_name}"
    )


    # =====================================================
    # BUTTONS
    # =====================================================

    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # GENERATE BUTTON
    # -----------------------------------------------------

    with col1:

        generate_clicked = st.button(
            "🚀 Generate Meeting Report"
        )


    # -----------------------------------------------------
    # DELETE BUTTON
    # -----------------------------------------------------

    with col2:

        delete_clicked = st.button(
            "🗑️ Delete Audio File"
        )


    # =====================================================
    # DELETE AUDIO
    # =====================================================

    if delete_clicked:

        # Delete temporary file if it exists
        if st.session_state.temp_audio_path:

            try:

                if os.path.exists(
                    st.session_state.temp_audio_path
                ):

                    os.remove(
                        st.session_state.temp_audio_path
                    )

            except Exception:
                pass


        # Clear audio
        st.session_state.audio_data = None

        st.session_state.audio_name = None

        # Clear transcript
        st.session_state.transcript = None

        # Clear report
        st.session_state.meeting_report = None

        # Clear processed file
        st.session_state.processed_file = None

        # Clear temporary path
        st.session_state.temp_audio_path = None


        st.success(
            "🗑️ Audio file deleted successfully."
        )

        st.rerun()


    # =====================================================
    # GENERATE REPORT
    # =====================================================

    if generate_clicked:

        extension = os.path.splitext(
            st.session_state.audio_name
        )[1]


        # -------------------------------------------------
        # SAVE TEMPORARY AUDIO
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(
                st.session_state.audio_data
            )

            temp_audio_path = temp_file.name


        st.session_state.temp_audio_path = (
            temp_audio_path
        )


        # =================================================
        # TRANSCRIPTION
        # =================================================

        with st.spinner(
            "🎧 Transcribing meeting audio..."
        ):

            try:

                transcript = transcribe_audio(
                    temp_audio_path
                )

                st.session_state.transcript = (
                    transcript
                )

            except Exception as e:

                st.error(
                    f"Transcription failed: {e}"
                )

                st.stop()


        # =================================================
        # SUMMARY
        # =================================================

        with st.spinner(
            "📝 Generating meeting report..."
        ):

            try:

                meeting_report = (
                    generate_meeting_summary(
                        transcript
                    )
                )

                st.session_state.meeting_report = (
                    meeting_report
                )

            except Exception as e:

                st.error(
                    f"Summary generation failed: {e}"
                )

                st.stop()


        st.success(
            "🎉 Meeting report generated successfully!"
        )


# =========================================================
# TRANSCRIPT
# =========================================================

if st.session_state.transcript:

    st.header("📝 Meeting Transcript")

    st.text_area(
        "Transcript",
        st.session_state.transcript,
        height=350
    )


# =========================================================
# MEETING REPORT
# =========================================================

if st.session_state.meeting_report:

    report = st.session_state.meeting_report

    st.header("📋 Meeting Report")


    # =====================================================
    # MEETING SUMMARY
    # =====================================================

    st.subheader("📌 Meeting Summary")


    if "## Key Decisions" in report:

        summary = report.split(
            "## Key Decisions",
            1
        )[0]

    else:

        summary = report


    st.markdown(summary)


    # =====================================================
    # KEY DECISIONS
    # =====================================================

    st.subheader("💡 Key Decisions")


    if "## Key Decisions" in report:

        decisions = report.split(
            "## Key Decisions",
            1
        )[1]


        if "## Action Items" in decisions:

            decisions = decisions.split(
                "## Action Items",
                1
            )[0]


        st.markdown(decisions)

    else:

        st.write(
            "No clear decisions identified."
        )


    # =====================================================
    # ACTION ITEMS
    # =====================================================

    st.subheader("✅ Action Items")


    if "## Action Items" in report:

        actions = report.split(
            "## Action Items",
            1
        )[1]

        st.markdown(actions)

    else:

        st.write(
            "No action items identified."
        )


    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.header("📥 Download Results")

    col1, col2 = st.columns(2)


    with col1:

        st.download_button(
            "📄 Download Transcript",
            st.session_state.transcript,
            file_name="meeting_transcript.txt",
            mime="text/plain",
            key="download_transcript"
        )


    with col2:

        st.download_button(
            "📋 Download Meeting Report",
            st.session_state.meeting_report,
            file_name="meeting_report.txt",
            mime="text/plain",
            key="download_report"
        )