import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import PyPDF2  # <-- NEW: Our PDF reader

load_dotenv()

st.set_page_config(page_title="Advanced AI Assistant", page_icon="🚀", layout="wide")

# Smart API Key Retrieval
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=api_key)

# --- 2. Sidebar & Settings ---
with st.sidebar:
    st.title("⚙️ AI Brain Settings")
    
    # --- NEW: PDF Uploader ---
    st.subheader("📚 Chat with your Data")
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    document_context = ""
    if uploaded_file is not None:
        # Read the PDF and extract the text
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            document_context += page.extract_text() + "\n"
        st.success("Document loaded successfully!")
    # -------------------------

    st.divider()

    system_prompt = st.text_area(
        "System Prompt (Persona)", 
        value="You are a highly intelligent, concise, and helpful AI assistant.", 
        height=150
    )
    
    temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state['messages'] = []
        st.rerun()

# --- 3. Chat Memory Setup ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# --- 4. The Upgraded API Function (Now with RAG!) ---
def api_calling(user_input, sys_prompt, temp, doc_context):
    
    # If a document is uploaded, inject it into the AI's hidden persona
    if doc_context != "":
        sys_prompt += f"\n\nHere is a document the user uploaded. Base your answers on this text:\n\n{doc_context}"

    api_messages = [{"role": "system", "content": sys_prompt}]
    
    for msg in st.session_state['messages']:
        api_messages.append(msg)
        
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

for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. Handle New User Input ---
if user_input := st.chat_input("Type your message here..."):
    
    with st.chat_message("user"):
        st.markdown(user_input)
        
    st.session_state['messages'].append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # We now pass the document context into the function!
            ai_response = api_calling(user_input, system_prompt, temperature, document_context)
            st.markdown(ai_response)
            
    st.session_state['messages'].append({"role": "assistant", "content": ai_response})