import os
from google import genai
from google.genai.types import GenerateContentConfig, Part
import streamlit as st

from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

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


# Function to display the chat history
def display_chat_history():
    for i, message in enumerate(st.session_state["chat_history"]):
        if message["sender"] == "user":
            with st.chat_message("user"):
                st.markdown(message["text"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["text"])


client = load_client()

# Main Streamlit app
st.title("Simple Chat App")

# Display chat history
display_chat_history()


def audio_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio_bytes = frame.to_ndarray().tobytes()
    st.session_state.audio_data = audio_bytes  # Store audio bytes
    return frame


st.title("Audio Recorder in Streamlit")
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

if webrtc_ctx.audio_receiver:
    st.write("Recording audio...")
    if hasattr(st.session_state, "audio_data"):
        st.audio(st.session_state.audio_data, format="audio/wav")
        st.write(f"Captured audio size: {len(st.session_state.audio_data)} bytes")

if webrtc_ctx.audio_receiver and hasattr(st.session_state, "audio_data"):
    st.audio(st.session_state.audio_data, format="audio/wav")

    user_input = Part.from_bytes(
        data=st.session_state.audio_data, mime_type="audio/wav"
    )
    # Add user message to chat history
    # st.session_state["chat_history"].append({"sender": "user", "text": user_input})

    # Display user message immediately
    # with st.chat_message("user"):
    #     st.markdown(user_input)

    # Simulate an assistant response (replace with your actual logic)
    assistant_response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_input,
        config=GenerateContentConfig(
            system_instruction="You are an empathetic nurse who is answering a patient's questions about their upcoming surgery. Translate the following text into Spanish.",
        ),
    ).text

    # Add assistant message to chat history
    st.session_state["chat_history"].append(
        {"sender": "assistant", "text": assistant_response}
    )

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    #  Rerun to update chat history
    st.rerun()  # important to force the display_chat_history() to update
