import streamlit as st
from langchain_groq import ChatGroq
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Document Intelligence", page_icon="📂", layout="wide")

# API Key Setup
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

# Initialize the LLM
llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

# --- Sidebar ---
with st.sidebar:
    st.title("📂 Document Settings")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    # Process PDF and store in session state
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            st.session_state['doc_text'] = content
            st.success("Document Loaded!")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Main App ---
st.title("🚀 Smart Assistant")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about your document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # If we have a document, give it to the AI as context
        if 'doc_text' in st.session_state:
            context = st.session_state['doc_text']
            # We "stuff" the context into the prompt safely
            full_prompt = f"Use this document text to answer: {context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
            
        with st.spinner("Thinking..."):
            response = llm.invoke(full_prompt)
            answer = response.content
            
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})