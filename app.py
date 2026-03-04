import os
import streamlit as st
import webbrowser
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS


# 🌱 Set page configuration
st.set_page_config(page_title="AGRITECH", page_icon="🌱", layout="wide")

# Store login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Google AI API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini AI model
try:
    model = genai.GenerativeModel("gemini-1.5-pro")
except Exception as e:
    st.error(f"Error initializing AI model: {e}")
    st.stop()

# Agritech-specific instructions
SYSTEM_PROMPT = """
You are Agritech AI assistant. You can:
1. Answer general questions about agriculture.
2. Provide guidance on farming techniques, pest control, irrigation, fertilizers, and climate-based farming.
3. Recommend pesticides, seeds, and fertilizers.
4. Provide guidance on farming machines, how to use the machines, and safety precautions.
5. You cannot browse the internet or answer non-agriculture-related questions.
"""

# Login page
def login():
    st.title("🌱 AGRITECH Login")
    username = st.text_input("Username / Email / Phone Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Please enter valid credentials!")

# Chat and voice interaction
def chat_interface():
    st.title("🌾 AGRITECH Chatboard")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you with agriculture today?"}
        ]

    # Sidebar: Chat history
    st.sidebar.title("Chat History")
    past_queries = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    if past_queries:
        for idx, query in enumerate(reversed(past_queries), 1):
            if st.sidebar.button(f"{idx}. {query[:30]}..."):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
    st.sidebar.markdown("---")

    # Show conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Telugu voice input
    st.markdown("#### 🎙️ Speak your question in Telugu")
    if st.button("🎤 Record in Telugu"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak in Telugu.")
            try:
                audio_data = recognizer.listen(source, timeout=5)
                query = recognizer.recognize_google(audio_data, language="te-IN")
                st.success(f"You said: {query}")
                handle_query(query, language="te")
            except sr.UnknownValueError:
                st.error("Sorry, could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Voice recognition failed: {e}")

    # Text input
    user_input = st.chat_input("Ask your agriculture-related question...")
    if user_input:
        handle_query(user_input, language="en")

# Handle query and generate response + voice
def handle_query(user_query, language="en"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(SYSTEM_PROMPT + f"\nUser: {user_query}")
                ai_response = response.text.strip()
            except Exception as e:
                ai_response = "Sorry, I am unable to answer your question."

            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.markdown(ai_response)

            # Voice output in Telugu if Telugu input
            try:
                tts = gTTS(text=ai_response, lang='te' if language == "te" else "en")
                tts.save("response.mp3")
                st.audio("response.mp3", format="audio/mp3")
            except Exception as e:
                st.warning("Failed to generate voice response.")

# Marketplace icon
def marketplace_icon():
    st.sidebar.markdown("### 🛒 Buy Agriculture Products")
    if st.sidebar.button("🛍️", help="Go to Marketplace"):
        webbrowser.open("https://www.bighaat.com/collections/organic-farming")

# Run the app
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login()
    else:
        chat_interface()
        marketplace_icon()
