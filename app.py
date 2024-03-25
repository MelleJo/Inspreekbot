import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import os
import tempfile

# Initialize OpenAI client with your API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def transcribe_audio(file_path):
    """
    Transcribe the audio file at file_path using OpenAI's Whisper model.
    """
    with open(file_path, "rb") as audio_file:
        try:
            response = openai.Audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            # Assuming 'text' directly contains the transcription
            transcript_text = response['text'] if 'text' in response else "Transcription text not found."
            return transcript_text
        except Exception as e:
            st.error(f"Transcription failed: {str(e)}")
            return None

st.title("Audio Transcription with OpenAI Whisper")

# Choice between uploading and recording audio
upload_or_record = st.radio("Do you want to upload audio or record?", ("Upload", "Record"))

if upload_or_record == "Upload":
    audio_upload = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac", "m4a", "mp4", "mpeg", "mpga", "oga", "ogg", "webm"])
    if audio_upload is not None:
        file_extension = os.path.splitext(audio_upload.name)[1][1:].lower()
        supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
        
        if file_extension in supported_formats:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
                temp_file.write(audio_upload.getvalue())
                temp_file_path = temp_file.name
            
            transcription_text = transcribe_audio(temp_file_path)
            st.text_area("Transcription", value=transcription_text, height=300)
            
            os.remove(temp_file_path)
        else:
            st.error(f"File format '{file_extension}' is not supported. Please upload a file in one of the following formats: {', '.join(supported_formats)}")

elif upload_or_record == "Record":
    audio_data = mic_recorder(
        key="recorder",
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        use_container_width=True,
        format="webm"
    )
    
    if audio_data and 'bytes' in audio_data:
        # Display the recorded audio
        st.audio(audio_data['bytes'], format='audio/webm')
        
        # Save recorded audio to temporary file for transcription
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(audio_data['bytes'])
            temp_file_path = temp_file.name
        
        if st.button('Transcribe'):
            transcription_text = transcribe_audio(temp_file_path)
            st.text_area("Transcription", value=transcription_text, height=300)
            
            os.remove(temp_file_path)
