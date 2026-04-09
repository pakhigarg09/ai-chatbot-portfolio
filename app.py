import streamlit as st
from groq import Groq
from streamlit_chat import message
import os
from dotenv import load_dotenv

load_dotenv()

# Smart API Key Retrieval
if "GROQ_API_KEY" in st.secrets:
    # If running on Streamlit Cloud, use this:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # If running locally on your computer, use this:
    api_key = os.environ.get("GROQ_API_KEY")

# Setup Groq Client
client = Groq(api_key=api_key)

# ... (the rest of your api_calling function and UI code stays exactly the same) ...

# 2. The API Calling Function using Llama 3 on Groq
def api_calling(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", # A lightning-fast, highly capable free model
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.5,
    )
    return response.choices[0].message.content

# 3. Streamlit UI Header
st.title("⚡ My Lightning Fast Chatbot")

# 4. Setup Session State (Memory)
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []

if 'ai_response' not in st.session_state:
    st.session_state['ai_response'] = []

# 5. Get User Input
user_input = st.text_input("Write here:", key="input")

# 6. Process the Input
if user_input:
    output = api_calling(user_input)
    
    st.session_state.user_input.append(user_input)
    st.session_state.ai_response.append(output)

# 7. Display the Chat History
if st.session_state['user_input']:
    for i in range(len(st.session_state['user_input']) - 1, -1, -1):
        message(st.session_state['ai_response'][i], 
                avatar_style="miniavs", 
                key=str(i) + 'bot')
                
        message(st.session_state["user_input"][i], 
                avatar_style="icons", 
                is_user=True, 
                key=str(i) + 'user')