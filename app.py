import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

if audio_upload is not None:
    audio_file = audio_upload.getvalue()
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    st.write(transcription)