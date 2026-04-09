import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# --- 1. Page Configuration (UX Upgrade) ---
st.set_page_config(page_title="Advanced AI Assistant", page_icon="🚀", layout="wide")

# Smart API Key Retrieval
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

# Setup Groq Client using the variable, NOT a string
client = Groq(api_key=api_key)

# --- 2. Sidebar & Settings (UX & Persona Upgrades) ---
with st.sidebar:
    st.title("⚙️ AI Brain Settings")
    st.markdown("Adjust how the AI behaves.")
    
    # Custom Persona Input
    system_prompt = st.text_area(
        "System Prompt (Persona)", 
        value="You are a highly intelligent, concise, and helpful AI assistant.", 
        height=150
    )
    
    # Temperature Slider
    temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    
    st.divider()
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat History"):
        st.session_state['messages'] = []
        st.rerun()

# --- 3. Chat Memory Setup ---
# We are changing how we store memory to be cleaner and match OpenAI/Groq standards
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# --- 4. The Upgraded API Function ---
def api_calling(user_input, sys_prompt, temp):
    # Start the memory list with the System Prompt (The Persona)
    api_messages = [{"role": "system", "content": sys_prompt}]
    
    # Attach all previous chat history so the AI remembers the conversation
    for msg in st.session_state['messages']:
        api_messages.append(msg)
        
    # Attach the user's newest message
    api_messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=api_messages,
        max_tokens=1024,
        temperature=temp,
    )
    return response.choices[0].message.content

# --- 5. Main Chat Interface ---
st.title("🚀 My Advanced Groq Assistant")

# Display all past messages using native Streamlit chat UI
for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. Handle New User Input ---
if user_input := st.chat_input("Type your message here..."):
    
    # Show user message instantly
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Save user message to memory
    st.session_state['messages'].append({"role": "user", "content": user_input})
    
    # Generate and show AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_response = api_calling(user_input, system_prompt, temperature)
            st.markdown(ai_response)
            
    # Save AI response to memory
    st.session_state['messages'].append({"role": "assistant", "content": ai_response})