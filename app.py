import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import io
import os

# Initialize OpenAI client with API key
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# UI for upload or record choice
upload_or_record = st.radio("Upload or record audio?", ("Upload", "Record"))

if upload_or_record == "Upload":
    audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])

elif upload_or_record == "Record":
    audio_data = mic_recorder(start_prompt="Start recording",
                              stop_prompt="Stop recording",
                              just_once=False,
                              use_container_width=True,
                              format="webm",
                              key="recorder")

    if audio_data and 'bytes' in audio_data:
        audio_upload = io.BytesIO(audio_data['bytes'])
    else:
        st.error("No audio data was found. Please ensure you have recorded something.")
        audio_upload = None

# Function to transcribe audio using OpenAI's Whisper API
def transcribe_audio(audio_file):
    if audio_file:
        try:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription
        except Exception as e:
            st.error(f"An error occurred during transcription: {str(e)}")
            return None
    else:
        return None

if audio_upload is not None:
    transcription_result = transcribe_audio(audio_upload)
    if transcription_result:
        st.write(transcription_result)
else:
    st.info("Please upload or record an audio file for transcription.")
