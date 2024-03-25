import streamlit as st
from openai import OpenAI
import os
import tempfile
import wave

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

upload_or_record = st.radio("Upload or Record Audio", ["Upload", "Record"])

if upload_or_record == "Upload":
    audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])

    if audio_upload is not None:
        file_extension = os.path.splitext(audio_upload.name)[1][1:].lower()
        supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

        if file_extension in supported_formats:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
                temp_file.write(audio_upload.getvalue())
                temp_file_path = temp_file.name

            with open(temp_file_path, "rb") as temp_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=temp_file
                )

            st.write(transcription)
            os.remove(temp_file_path)
        else:
            st.error(f"File format '{file_extension}' is not supported. Please upload a file in one of the following formats: {', '.join(supported_formats)}")

elif upload_or_record == "Record":
    recorded_audio = st.audio_recorder("Record your voice")

    if recorded_audio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            with wave.open(temp_file.name, "wb") as wave_file:
                wave_file.setnchannels(1)
                wave_file.setsampwidth(2)
                wave_file.setframerate(16000)
                wave_file.writeframes(recorded_audio.to_bytes())
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as temp_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=temp_file
            )

        st.write(transcription)
        os.remove(temp_file_path)