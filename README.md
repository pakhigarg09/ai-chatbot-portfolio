# ⚡ Lightning Fast AI Chatbot

A highly responsive, web-based conversational AI application. This project demonstrates how to integrate modern Large Language Models (LLMs) into a clean, user-friendly web interface.

## 🛠️ Tech Stack
* **Frontend/UI:** Streamlit (Python)
* **AI Engine:** Meta Llama 3.1 (8B-Instant)
* **API Provider:** Groq (for ultra-low latency inference)
* **Environment Management:** `python-dotenv` for secure key handling

## ✨ Features
* **Real-time Chat:** Near-instantaneous text generation using Groq's LPU infrastructure.
* **Session Memory:** Retains conversation history context during the active session.
* **Secure Architecture:** API keys are hidden and managed via environment variables.

## 🚀 How to Run Locally
1. Clone this repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add your Groq API key: `GROQ_API_KEY=your_key_here`
4. Run the app: `python -m streamlit run app.py`