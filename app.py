import streamlit as st
import sounddevice as sd
import numpy as np
import io
import wave

import os
from google import genai
from google.genai.types import GenerateContentConfig, Part
from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core.client_options import ClientOptions


# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION")

if PROJECT_ID and not LOCATION:
    LOCATION = "us-central1"

MODEL_ID = "gemini-2.0-flash-lite"


@st.cache_resource
def load_client() -> genai.Client:
    """Load Google Gen AI Client."""
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


@st.cache_resource
def load_tts_client() -> genai.Client:
    """Load Google Gen AI Client."""
    return texttospeech.TextToSpeechClient(
        client_options=ClientOptions(api_endpoint="us-texttospeech.googleapis.com")
    )


client = load_client()

tts_client = load_tts_client()


def record_audio(duration, sample_rate):
    """Records audio from the microphone."""
    try:
        with st.spinner(f"Recording for {duration} seconds..."):
            audio = sd.rec(
                int(duration * sample_rate), samplerate=sample_rate, channels=1
            )  # Force to mono
            sd.wait()  # Wait until recording is finished
        st.success("Recording complete!")
        return audio
    except Exception as e:
        st.error(f"Error during recording: {e}")
        return None


def get_audio_bytes(audio, sample_rate):
    """Converts the audio data to bytes in WAV format."""
    try:
        # Convert to 16-bit PCM (required for most audio players)
        audio_int16 = np.int16(audio * 32767)  # Scale to -32768 to 32767

        # Save as WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes for 16-bit PCM
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        buffer.seek(0)  # Reset to beginning of buffer
        audio_bytes = buffer.read()  # Read the bytes from the buffer
        return audio_bytes
    except Exception as e:
        st.error(f"Error converting audio to bytes: {e}")
        return None


def play_audio(audio_bytes):
    """Plays the audio from a byte stream."""
    if audio_bytes is not None:
        try:
            st.audio(audio_bytes, format="audio/wav", autoplay=True)
        except Exception as e:
            st.error(f"Error playing audio: {e}")


def generate_audio(text, language="es-US") -> bytes:
    """Generates audio from text using Google Cloud Text-to-Speech."""
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(
            language_code=language,
            name="es-US-Chirp-HD-D" if language == "es-US" else "en-US-Casual-K",
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        ),
    )
    return response.audio_content


def main():
    st.title("HCA Translator")

    # Add radio button for language direction
    target_language = st.radio(
        "Patient Language (lenguaje del paciente)",
        ("Spanish (Español)", "English (Inglés)"),
    )

    duration = st.slider("Recording duration (seconds)", 1, 10, 3)  # Default 3 seconds
    sample_rate = 44100  # Standard audio sample rate

    if st.button("Start Recording"):
        audio = record_audio(duration, sample_rate)

        if audio is not None:
            audio_bytes = get_audio_bytes(audio, sample_rate)

            user_input = Part.from_bytes(data=audio_bytes, mime_type="audio/wav")

            instruction = f"Translate the following audio into {target_language}. Only respond with the translation."

            if target_language == "Spanish (Español)":
                audio_language = "es-US"
            else:
                audio_language = "en-US"

            assistant_response = client.models.generate_content(
                model=MODEL_ID,
                contents=[instruction, user_input],
                config=GenerateContentConfig(
                    system_instruction="You are a kind, empathetic nurse who is answering a patient's questions.",
                ),
            ).text

            with st.chat_message("assistant"):
                st.markdown(assistant_response)

            output_audio_bytes = generate_audio(assistant_response, audio_language)

            if output_audio_bytes:
                play_audio(output_audio_bytes)


if __name__ == "__main__":
    main()
