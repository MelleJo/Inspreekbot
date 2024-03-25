import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import os
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# UI for upload or record choice
upload_or_record = st.radio("Upload or record audio?", ("Upload", "Record"))
audio_upload = None  # Initialize to avoid reference errors

if upload_or_record == "Upload":
    audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])

# Handling the Recorded Audio
if upload_or_record == "Record":
    audio_data = mic_recorder(start_prompt="Start recording",
                              stop_prompt="Stop recording",
                              just_once=False,
                              use_container_width=True,
                              format="webm",
                              key="recorder")

    # Check if recording was successful and data is not None
    if audio_data is not None and audio_data.get("blob") is not None:
        audio_blob = audio_data.get("blob")

        # Convert the audio blob to a BytesIO object
        import base64
        import io
        audio_bytes = base64.b64decode(audio_blob.split(",")[1])
        audio_upload = io.BytesIO(audio_bytes)
    else:
        st.error("No audio data was found. Please ensure you have recorded something.")



def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        temp_file.write(audio_file.read())
        temp_file_path = temp_file.name

    # Convert to appropriate format if necessary before sending for transcription
    # Additional conversion logic might be required here

    with open(temp_file_path, "rb") as temp_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=temp_file
        )
    
    os.remove(temp_file_path)
    return transcription

if audio_upload is not None:
    try:
        transcription_result = transcribe_audio(audio_upload)
        st.write(transcription_result)
    except Exception as e:
        st.error(f"An error occurred during transcription: {str(e)}")
else:
    st.info("Please upload or record an audio file for transcription.")
