import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])

if audio_upload is not None:
    file_extension = os.path.splitext(audio_upload.name)[1][1:].lower()
    supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

    if file_extension in supported_formats:
        audio_file = audio_upload.getvalue()
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

        st.write(transcription)
    else:
        st.error(f"File format '{file_extension}' is not supported. Please upload a file in one of the following formats: {', '.join(supported_formats)}")