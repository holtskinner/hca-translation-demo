import streamlit as st
import sounddevice as sd
import numpy as np
import io
import wave
import tempfile


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


def play_audio(audio, sample_rate):
    """Plays the recorded audio."""
    if audio is not None:
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

            st.audio(buffer, format="audio/wav")
        except Exception as e:
            st.error(f"Error playing audio: {e}")


def main():
    st.title("HCA Translator")

    duration = st.slider("Recording duration (seconds)", 1, 10, 3)  # Default 3 seconds
    sample_rate = 44100  # Standard audio sample rate

    if st.button("Start Recording"):
        audio = record_audio(duration, sample_rate)

        if audio is not None:
            st.write("Playing back the recording:")
            play_audio(audio, sample_rate)


if __name__ == "__main__":
    main()
