import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def transcribe_audio(file_path):
    """ Transcribes the audio file using OpenAI's Whisper model. """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcribe("whisper-1", audio_file)
            transcript_text = transcript["text"]
            return transcript_text
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return "Transcription failed."

st.title("Audio Transcription with OpenAI Whisper")

# Choose between uploading and recording audio
upload_or_record = st.radio("Do you want to upload audio or record?", ("Upload", "Record"))

if upload_or_record == "Upload":
    uploaded_audio = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
    if uploaded_audio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_audio.name)[1]) as tmp_audio:
            tmp_audio.write(uploaded_audio.getvalue())
            transcription_text = transcribe_audio(tmp_audio.name)
            st.text_area("Transcription", value=transcription_text, height=300)
            os.remove(tmp_audio.name)

elif upload_or_record == "Record":
    audio_data = mic_recorder(
        key="recorder",
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        use_container_width=True,
        format="webm"
    )
    if audio_data and 'bytes' in audio_data:
        st.audio(audio_data['bytes'], format='audio/webm')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
            tmp_audio.write(audio_data['bytes'])
            if st.button('Transcribe Recorded Audio'):
                transcription_text = transcribe_audio(tmp_audio.name)
                st.text_area("Transcription", value=transcription_text, height=300)
                os.remove(tmp_audio.name)
