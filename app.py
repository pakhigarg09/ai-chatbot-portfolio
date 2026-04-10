import streamlit as st
from langchain_groq import ChatGroq
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- 1. Page Config & Persona ---
st.set_page_config(page_title="Interior AI Advisor", page_icon="🏠")

# The "System Persona" - This is your secret sauce as an Architect
DESIGN_CONTEXT = """
You are an expert Interior Design Assistant with a background in Architecture. 
Your goal is to help users with:
1. Space planning and furniture layouts.
2. Color palettes and material suggestions (woods, metals, fabrics).
3. Style identification (Modern, Mid-Century, Scandinavian, Industrial, etc.).
4. Budget-friendly alternatives.
Always ask follow-up questions about room dimensions, natural lighting, and lifestyle if the user is vague.
"""

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

# --- 2. Logging Function (PM Feature) ---
def log_interaction(user_msg, ai_res):
    file_exists = os.path.isfile('chat_logs.csv')
    with open('chat_logs.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'User_Input', 'AI_Response'])
        writer.writerow([datetime.now(), user_msg, ai_res])

# --- 3. UI Sidebar ---
with st.sidebar:
    st.title("🏠 Design Studio")
    st.info("I use your room type, style, and budget to give tailored advice.")
    
    # Download Logs button for your PM portfolio
    if os.path.exists('chat_logs.csv'):
        with open('chat_logs.csv', 'rb') as f:
            st.download_button("📊 Download Chat Logs (CSV)", f, "chat_logs.csv", "text/csv")

    if st.button("🗑️ Reset Consultation"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Chat Logic ---
st.title("✨ Interior Design AI Advisor")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Help me design a cozy 12x12 bedroom with a $2000 budget"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Combine Persona + History + User Input
        full_prompt = f"{DESIGN_CONTEXT}\n\nUser Question: {prompt}"
        
        with st.spinner("Designing your space..."):
            response = llm.invoke(full_prompt)
            answer = response.content
            
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log it for analysis
        log_interaction(prompt, answer)