import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
from pydub import AudioSegment
import io

# Initialize OpenAI client with your API key
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# UI for choosing between upload or record
upload_or_record = st.radio("Upload or record audio?", ("Upload", "Record"))
audio_file_io = None  # Initialize audio_file_io

# Handle file upload
if upload_or_record == "Upload":
    audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])
    if audio_upload:
        audio_bytes = audio_upload.read()
        audio_file_io = io.BytesIO(audio_bytes)
elif upload_or_record == "Record":
    # Handle audio recording
    audio_data = mic_recorder(start_prompt="Start recording",
                              stop_prompt="Stop recording",
                              just_once=False,
                              use_container_width=True,
                              format="webm",
                              key="recorder")
    if audio_data and 'bytes' in audio_data:
        audio_file_io = io.BytesIO(audio_data['bytes'])

# Define function to convert audio to WAV format
# Ensure this function checks if audio_file_io is not None
def convert_audio_to_wav(audio_bytes_io):
    if audio_bytes_io:
        audio = AudioSegment.from_file(audio_bytes_io, format="webm")
        audio_io = io.BytesIO()
        audio.export(audio_io, format="wav")
        audio_io.seek(0)
        return audio_io

# Transcribe audio if audio_file_io is not None
if audio_file_io:
    audio_file_io_wav = convert_audio_to_wav(audio_file_io)
    if audio_file_io_wav:  # Check if conversion was successful
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_io_wav
        )
        st.write(transcription)
else:
    st.info("Please upload or record an audio file for transcription.")
