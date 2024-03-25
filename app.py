import streamlit as st
import openai
import io

# Assuming OpenAI API key is set in Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

def transcribe_audio(audio_bytes):
    """
    Transcribe audio using OpenAI's Whisper model.
    """
    audio_bio = io.BytesIO(audio_bytes)
    audio_bio.name = 'audio.webm'
    try:
        # Sending the audio file to OpenAI for transcription
        response = openai.Audio.create(
            audio=audio_bio,
            model="whisper-1"
        )
        
        # OpenAI's Whisper model returns the transcription in 'text' field directly
        # Check if the response includes the expected 'text' field
        if 'text' in response:
            transcript_text = response['text']
        else:
            # Log for debugging
            print("Transcription response structure:", response)
            transcript_text = "Transcription text not found."
        
        return transcript_text
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None

# UI components for recording or uploading audio for transcription
upload_or_record = st.radio("Do you want to upload audio or record?", ("Upload", "Record"))

if upload_or_record == "Upload":
    uploaded_file = st.file_uploader("Choose an audio file", type=["webm", "mp3", "wav", "ogg", "m4a"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        transcript = transcribe_audio(bytes_data)
        st.text_area("Transcription", value=transcript, height=300)
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
        
        if st.button('Transcribe'):
            transcript = transcribe_audio(audio_data['bytes'])
            st.text_area("Transcription", value=transcript, height=300)
