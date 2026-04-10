import streamlit as st
from langchain_groq import ChatGroq
import PyPDF2
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- 1. Page Configuration & CSS ---
st.set_page_config(page_title="InteriorAI Advisor", page_icon="📐", layout="wide")

# API Key Setup
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

# --- 2. Session State Initialization ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0

# --- 3. Sidebar: Design Studio & Analytics ---
with st.sidebar:
    st.title("📐 Design Studio Setup")
    st.markdown("Upload floor plans or client briefs (PDF).")
    
    uploaded_file = st.file_uploader("Upload Reference Document", type="pdf")
    if uploaded_file:
        with st.spinner("Analyzing site data..."):
            reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            st.session_state['doc_text'] = content
            st.success("Site Data Loaded!")

    st.divider()
    
    # Custom Persona
    system_prompt = st.text_area(
        "AI Persona Instructions", 
        value="You are an expert Architect and Interior Designer. Provide practical, creative advice on space planning, palettes, and furniture. If the user hasn't provided a document, politely ask them to describe their space or upload a floor plan.",
        height=120
    )
    temp = st.slider("Design Creativity (Temperature)", 0.0, 1.0, 0.7)

    st.divider()
    
    # --- PM Analytics Dashboard ---
    st.subheader("📊 PM Analytics")
    st.metric(label="Total Tokens Used", value=st.session_state.total_tokens)
    
    if st.button("📥 Export Chat Logs (CSV)"):
        if st.session_state.log_data:
            df = pd.DataFrame(st.session_state.log_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "design_session_logs.csv", "text/csv")
        else:
            st.warning("No data to export.")
            
    if st.button("🗑️ Reset Session"):
        st.session_state.messages = []
        st.session_state.log_data = []
        st.session_state.total_tokens = 0
        if 'doc_text' in st.session_state:
            del st.session_state['doc_text']
        st.rerun()

# --- 4. Main Chat Interface ---
st.title("🛋️ AI Interior Design Advisor")

# The "Empty State" Welcome Message
if len(st.session_state.messages) == 0:
    st.info("""
    **Welcome to the Design Studio!** 👋  
    To get the best results:
    1. Upload a PDF floor plan or site notes in the sidebar.
    2. Tell me your budget, preferred style (e.g., Japandi, Mid-Century), and the room type.
    """)

# Render past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. AI Interaction Logic ---
if prompt := st.chat_input("Ex: 'Suggest a layout for a 200 sq ft bedroom...'"):
    # Render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        full_context = system_prompt
        if 'doc_text' in st.session_state:
            full_context += f"\n\nContext from Uploaded Document: {st.session_state['doc_text']}"
        
        full_query = f"{full_context}\n\nUser Request: {prompt}"
        
        with st.spinner("Drafting design concepts..."):
            # We use invoke and capture the response metadata for our Token Tracker!
            response = llm.invoke(full_query)
            answer = response.content
            
            # Extract token usage (The PM Flex)
            tokens_used = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
            st.session_state.total_tokens += tokens_used
            
            st.markdown(answer)
            
            # Log data
            st.session_state.log_data.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_query": prompt,
                "ai_response": answer,
                "tokens_consumed": tokens_used
            })
            
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun() # Force a quick refresh to update the Token Counter in the sidebar!