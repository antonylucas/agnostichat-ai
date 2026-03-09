import os

import requests
import streamlit as st

st.title("CodeLlama SQL/Elasticsearch Query Generator")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# System prompt for SQL/Elasticsearch query generation
SYSTEM_PROMPT = """You are an expert SQL and Elasticsearch query generator.
Your task is to help users generate accurate and efficient queries based on their requirements.
When generating queries:
1. Consider performance optimization
2. Include proper error handling
3. Follow best practices for the specific query type
4. Provide explanations for complex query parts"""

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Describe the query you need (SQL or Elasticsearch)?"):
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
            "model": "codellama:13b-instruct",
            "prompt": f"{SYSTEM_PROMPT}\n\nUser: {prompt}\nAssistant:",
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024},
        },
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
