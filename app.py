import streamlit as st
from groq import Groq
import os

# Page configuration
st.set_page_config(
    page_title="Groq AI Chat",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 Groq AI Chat Application")
st.markdown("Chat with AI using Groq's free models")

# Sidebar for API key and model selection
with st.sidebar:
    st.header("Configuration")
    
    # Initialize session state for API key
    if "GROQ_API_KEY" not in st.session_state:
        st.session_state.GROQ_API_KEY = ""
    
    # API Key input
    st.session_state.GROQ_API_KEY = st.text_input(
        "Enter your Groq API Key:",
        type="password",
        value=st.session_state.GROQ_API_KEY,
        help="Get your free API key from https://console.groq.com"
    )
    
    # Model selection
    model_option = st.selectbox(
        "Select Model:",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ],
        help="Choose the AI model for your chat"
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1
    )
    
    # Max tokens slider
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=256,
        max_value=8192,
        value=1024,
        step=256
    )
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses Groq's fast inference API with open-source models.")
    st.markdown("[Get your free API key](https://console.groq.com)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    if not st.session_state.GROQ_API_KEY:
        st.error("⚠️ Please enter your Groq API key in the sidebar!")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Initialize Groq client with GROQ_API_KEY
            client = Groq(api_key=st.session_state.GROQ_API_KEY)
            
            # Create chat completion with streaming
            stream = client.chat.completions.create(
                model=model_option,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Make sure your API key is valid and you have internet connection.")
            full_response = f"Error: {str(e)}"
    
    # Add assistant response to chat history
    if full_response and not full_response.startswith("Error:"):
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by Groq API | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
