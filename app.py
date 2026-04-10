import streamlit as st
from langchain_groq import ChatGroq
import PyPDF2
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- 1. Page Configuration ---
st.set_page_config(page_title="InteriorAI Advisor", page_icon="🏠", layout="wide")

# API Key Setup
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

# --- 2. Sidebar: Design Studio Settings ---
with st.sidebar:
    st.title("🏠 Design Studio")
    st.markdown("Upload floor plans, style guides, or site notes (PDF).")
    
    uploaded_file = st.file_uploader("Upload PDF Reference", type="pdf")
    if uploaded_file:
        reader = PyPDF2.PdfReader(uploaded_file)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        st.session_state['doc_text'] = content
        st.success("Reference Loaded!")

    st.divider()
    
    # Custom Persona for Architecture/Interiors
    system_prompt = st.text_area(
        "AI Designer Persona", 
        value="You are an expert Interior Designer and Architect. Your goal is to provide advice on space planning, color palettes, furniture styles, and lighting based on the user's budget and room type. Be professional, creative, and practical.",
        height=150
    )
    
    temp = st.slider("Design Creativity", 0.0, 1.0, 0.7)

    # --- Metrics Export for your PRD ---
    st.divider()
    if st.button("📊 Export Chat Logs for PRD"):
        if 'log_data' in st.session_state and st.session_state.log_data:
            df = pd.DataFrame(st.session_state.log_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "design_assistant_logs.csv", "text/csv")
        else:
            st.warning("No chat data to export yet!")

# --- 3. Chat Logic & RAG ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []

st.title("🛋️ Interior Design Advisor")
st.info("Ask me about room layouts, color schemes, or upload a floor plan to get started.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: 'Suggest a Japandi style living room layout for a small apartment.'"):
    # Log User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Inject PDF context if available
        full_context = system_prompt
        if 'doc_text' in st.session_state:
            full_context += f"\n\nReference Document Context: {st.session_state['doc_text']}"
        
        full_query = f"{full_context}\n\nUser Question: {prompt}"
        
        with st.spinner("Visualizing..."):
            response = llm.invoke(full_query)
            answer = response.content
            st.markdown(answer)
            
            # Log Data for PM Metrics
            st.session_state.log_data.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_query": prompt,
                "ai_response": answer,
                "creativity_setting": temp
            })
            
    st.session_state.messages.append({"role": "assistant", "content": answer})