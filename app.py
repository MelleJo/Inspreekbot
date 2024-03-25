import streamlit as st
from openai import OpenAI

client = OpenAI()

audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

audio_file = open(audio_upload)
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)

st.write(transcription)
