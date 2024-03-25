import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import io

# Function to initialize OpenAI client and transcribe audio
def transcribe_audio(audio_bytes, openai_api_key):
    openai_client = openai.OpenAI(api_key=openai_api_key)
    audio_bio = io.BytesIO(audio_bytes)
    audio_bio.name = 'audio.webm'
    try:
        # Create transcription
        transcription_response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_bio
        )
        
        # Assuming the transcription text can be accessed directly (adjust as necessary)
        # Check the OpenAI API documentation or inspect the transcription_response object for the correct field
        transcript_text = transcription_response['text'] if 'text' in transcription_response else "Transcription text not found."
        return transcript_text
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None


# Streamlit UI
st.title("Audio Transcription App")

# Load OpenAI API key
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Record or upload audio
upload_or_record = st.radio("Do you want to upload audio or record?", ("Upload", "Record"))

if upload_or_record == "Upload":
    uploaded_file = st.file_uploader("Choose an audio file", type=["webm", "mp3", "wav", "ogg", "m4a"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        transcript = transcribe_audio(bytes_data, openai_api_key)
        if transcript:
            st.text(transcript)
        else:
            st.write("Upload a file to see the transcription.")
elif upload_or_record == "Record":
    audio_data = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=False,
        use_container_width=True,
        format="webm",
        key="recorder"
    )
    
    if audio_data and 'bytes' in audio_data:
        st.audio(audio_data['bytes'], format='audio/webm')
        if st.button('Transcribe'):
            transcript = transcribe_audio(audio_data['bytes'], openai_api_key)
            if transcript:
                st.text(transcript)
            else:
                st.write("Please record something to transcribe.")
    else:
        st.write("Click 'Start recording' to record audio.")
