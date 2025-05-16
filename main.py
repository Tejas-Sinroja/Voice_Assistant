import streamlit as st
import time
import time
from openai import OpenAI
import os
import io
from streamlit_mic_recorder import mic_recorder

# Initialize session state for API key if it doesn't exist
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

def setup_sidebar():
    """Configure the sidebar with options."""
    with st.sidebar:
        st.title("Key Settings")
        st.markdown("------")
        st.session_state.openai_api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password"
        )
        st.markdown("------")
        st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and [OpenAI](https://openai.com/)")

def process_audio_and_query(audio_file, query, api_key):
    """Processes the audio file and user query using OpenAI APIs."""
    if not api_key:
        st.error("OpenAI API key is not set.")
        return None

    try:
        client = OpenAI(api_key=api_key)

        # Transcribe the audio file
        with st.spinner("Transcribing audio..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", # Corrected model name
                file=audio_file
            )
        st.success("Transcription completed successfully!")
        st.markdown("### Transcription")
        st.write(transcript.text)

        # Use the transcription to answer the query
        with st.spinner("Fetching response from OpenAI..."):
            messages = [
                {"role": "system", "content": "You are a helpful voice assistant. Answer the user's question based on the provided audio transcription."},
                {"role": "user", "content": f"Based on the following transcription, answer this question: '{query}'\n\nTranscription:\n{transcript.text}"}
            ]
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Corrected model name
                messages=messages
            )
        st.success("Response fetched successfully!")
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- Main Application ---
st.set_page_config(page_title="Voice Assistant", page_icon=":robot_face:", layout="wide")
st.title("Voice Assistant 🎙️")
st.info("Upload an audio file (MP3) and ask a question about its content.")

setup_sidebar()

if not st.session_state.openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to proceed.")
else:
    st.subheader("Upload an audio file or record from your microphone")

    audio_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

    st.markdown("---") # Add a separator

    # Mic recorder component
    recorded_audio_result = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        just_once=True,
        key="mic_recorder"
    )

    audio_input = None
    if audio_file:
        audio_input = audio_file
    elif recorded_audio_result and recorded_audio_result.get('bytes'):
        audio_input = io.BytesIO(recorded_audio_result['bytes'])
        audio_input.name = "recorded_audio.wav" # Give it a name for the API
        st.success("Recording complete.") # Indicate completion

        # Display recorded audio and download button immediately
        st.audio(audio_input, format='audio/wav')
        st.download_button(
            label="Download Recording",
            data=recorded_audio_result['bytes'],
            file_name="recorded_audio.wav",
            mime="audio/wav"
        )

    query = st.text_input(
        "What would you like to know about the audio?",
        placeholder="e.g., Summarize the key points.",
    )

    # Process audio if available and query is entered
    if audio_input and query:
        response_content = process_audio_and_query(audio_input, query, st.session_state.openai_api_key)
        if response_content:
            st.markdown("## Response")
            st.write(response_content)
    elif audio_input and not query:
        st.info("Please enter a question about the audio.")
    elif not audio_input and query:
         st.info("Please upload an audio file or record audio.")
