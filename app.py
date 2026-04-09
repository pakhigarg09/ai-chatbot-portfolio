import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Enterprise RAG Assistant", page_icon="🏢", layout="wide")

# API Key Setup
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.environ.get("GROQ_API_KEY")

# Initialize the LLM (LangChain version)
llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

# --- Sidebar ---
with st.sidebar:
    st.title("🏢 Enterprise Settings")
    uploaded_file = st.file_uploader("Upload large PDFs", type="pdf")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- The RAG Logic ---
# We use st.cache_resource so the PDF is only processed once!
@st.cache_resource
def process_pdf(file):
    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(file.getbuffer())
    
    loader = PyPDFLoader("temp.pdf")
    docs = loader.load()
    
    # Chunking: Breaking the doc into small pieces
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    
    # Embeddings: Turning text into numbers (Vectors)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Vector Store: Our searchable database
    vector_store = FAISS.from_documents(final_documents, embeddings)
    return vector_store

# --- Main App ---
st.title("📂 Advanced Document Intelligence")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Process the file if uploaded
vector_db = None
if uploaded_file:
    with st.spinner("Indexing document into Vector DB..."):
        vector_db = process_pdf(uploaded_file)
        st.sidebar.success("Vector Database Ready!")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask anything about the document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if vector_db:
            # Create the retrieval chain
            prompt_template = ChatPromptTemplate.from_template(
                """Answer the questions based on the provided context only.
                <context>
                {context}
                <context>
                Question: {input}"""
            )
            
            document_chain = create_stuff_documents_chain(llm, prompt_template)
            retriever = vector_db.as_retriever()
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            response = retrieval_chain.invoke({"input": prompt})
            answer = response['answer']
        else:
            # Fallback to normal chat if no PDF
            response = llm.invoke(prompt)
            answer = response.content
            
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})