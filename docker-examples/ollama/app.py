import streamlit as st
import requests
import os

st.title("Ollama Chat Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Ollama response
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    response = requests.post(
        f"{ollama_host}/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        assistant_response = response.json()["response"]
    else:
        assistant_response = "Sorry, I encountered an error while processing your request."

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(assistant_response) 