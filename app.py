import streamlit as st
from openai import OpenAI
import os
import tempfile
import wave
import base64
import time

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
    st.write("Click the 'Start Recording' button to begin recording your voice.")
    start_recording = st.button("Start Recording")

    if start_recording:
        st.write("Recording...")

        # Record audio using JavaScript
        recorded_audio = st.pyplot(record_audio())

        if recorded_audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                with wave.open(temp_file.name, "wb") as wave_file:
                    wave_file.setnchannels(1)
                    wave_file.setsampwidth(2)
                    wave_file.setframerate(16000)
                    wave_file.writeframes(base64.b64decode(recorded_audio.split(",")[1]))
                temp_file_path = temp_file.name

            with open(temp_file_path, "rb") as temp_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=temp_file
                )

            st.write(transcription)
            os.remove(temp_file_path)

@st.cache_data
def record_audio():
    """
    JavaScript function to record audio from the user's microphone.
    """
    recording_stopped = False
    audio_data = None

    def streamlit_audio_recorder(max_seconds=None):
        """
        This function is called by the JavaScript code to start the recording.
        """
        nonlocal recording_stopped, audio_data

        if max_seconds is not None:
            st.write(f"Recording will stop after {max_seconds} seconds.")

        recording_stopped = False
        audio_data = None

        def stop_recording():
            """
            This function is called by the JavaScript code to stop the recording.
            """
            nonlocal recording_stopped, audio_data
            recording_stopped = True
            return audio_data

        return stop_recording

    # JavaScript code to record audio
    js_code = """
        const handleSuccess = function(stream) {
            const options = {mimeType: 'audio/webm'};
            const recordedChunks = [];
            const mediaRecorder = new MediaRecorder(stream, options);

            mediaRecorder.addEventListener('dataavailable', function(e) {
                if (e.data.size > 0) {
                    recordedChunks.push(e.data);
                }
            });

            mediaRecorder.addEventListener('stop', function() {
                const audioBlob = new Blob(recordedChunks);
                const reader = new FileReader();
                reader.addEventListener('loadend', function() {
                    const base64String = reader.result.split(',')[1];
                    Streamlit.setComponentValue(base64String);
                });
                reader.readAsDataURL(audioBlob);
            });

            const stopRecording = Streamlit.setComponentReady(mediaRecorder.start.bind(mediaRecorder));
            setTimeout(function() {
                stopRecording(null);
                mediaRecorder.stop();
            }, %s * 1000);
        };

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(handleSuccess);
    """ % st.session_state.get("max_recording_time", 10)

    # Record audio for a maximum of 10 seconds (can be changed)
    st.session_state["max_recording_time"] = 10

    # Create a container to hold the audio recorder
    container = st.container()
    with container:
        # Display the audio recorder using st.pyplot
        stop_recording = streamlit_audio_recorder(st.session_state["max_recording_time"])
        time.sleep(0.1)
        st.markdown(f'<script>{js_code}</script>', unsafe_allow_html=True)

    while not recording_stopped:
        time.sleep(0.1)

    if audio_data is not None:
        return audio_data