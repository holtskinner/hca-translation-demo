import streamlit as st

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# Function to display the chat history
def display_chat_history():
    for i, message in enumerate(st.session_state["chat_history"]):
        if message["sender"] == "user":
            with st.chat_message("user"):
                st.markdown(message["text"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["text"])


# Main Streamlit app
st.title("Simple Chat App")

# Display chat history
display_chat_history()

# Chat input
user_input = st.chat_input("Say something:")

if user_input:
    # Add user message to chat history
    st.session_state["chat_history"].append({"sender": "user", "text": user_input})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Simulate an assistant response (replace with your actual logic)
    assistant_response = f"You said: {user_input}  (This is a placeholder response.)"  # Replace this with your AI model response
    # Add artificial delay
    # import time
    # time.sleep(1)

    # Add assistant message to chat history
    st.session_state["chat_history"].append(
        {"sender": "assistant", "text": assistant_response}
    )

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    #  Rerun to update chat history
    st.rerun()  # important to force the display_chat_history() to update
