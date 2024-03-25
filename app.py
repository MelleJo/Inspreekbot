import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import io

# Ensure the OpenAI API key is correctly set in your Streamlit app's secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

def transcribe_audio(audio_bytes):
    """
    Transcribe audio using OpenAI's updated Whisper model API.
    """
    audio_bio = io.BytesIO(audio_bytes)
    try:
        # Sending the audio file to OpenAI for transcription using the correct API call
        response = openai.Audio.transcriptions.create(
            model="whisper-1", 
            file=audio_bio
        )
        
        # Extracting the transcription text from the response
        if 'data' in response and len(response['data']) > 0 and 'text' in response['data'][0]:
            transcript_text = response['data'][0]['text']
        else:
            transcript_text = "Transcription text not found."
        
        return transcript_text
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None

st.title("Audio Transcription with OpenAI Whisper")

upload_or_record = st.radio("Do you want to upload audio or record?", ("Upload", "Record"))

if upload_or_record == "Record":
    audio_data = mic_recorder(start_prompt="Start recording",
                              stop_prompt="Stop recording",
                              use_container_width=True,
                              format="webm",
                              key="recorder")
    if audio_data and 'bytes' in audio_data:
        st.audio(audio_data['bytes'], format='audio/webm')
        if st.button('Transcribe'):
            transcript = transcribe_audio(audio_data['bytes'])
            st.text_area("Transcription", value=transcript, height=300)
elif upload_or_record == "Upload":
    uploaded_file = st.file_uploader("Choose an audio file", type=["webm", "mp3", "wav", "ogg", "m4a"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        transcript = transcribe_audio(bytes_data)
        st.text_area("Transcription", value=transcript, height=300)
