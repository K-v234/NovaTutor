import gradio as gr
import requests
from googlesearch import search
import speech_recognition as sr
from gtts import gTTS
import os
import chromadb

# Initialize ChromaDB for self-learning
chroma_client = chromadb.PersistentClient()
collection = chroma_client.get_or_create_collection(name="ai_tutor")

def google_search(query):
    """Performs a Google search and returns the top 3 results."""
    results = []
    for url in search(query, num=3, stop=3, pause=2):
        results.append(url)
    return "\n".join(results) if results else "No results found."

def ai_tutor(question):
    """Processes the user's question and returns an AI-generated response."""
    results = collection.get(where={"question": question})
    existing_answer = results.get("documents", [])
    
    if existing_answer:
        return existing_answer[0]
    
    if "stock price" in question.lower() or "current" in question.lower():
        answer = google_search(question)
    else:
        answer = f"You asked: {question}. Here's what I found: {google_search(question)}"
    
    collection.add(documents=[answer], metadatas=[{"question": question}], ids=[str(len(collection))])
    return answer

def text_to_speech(text):
    """Converts text to speech using Google TTS."""
    tts = gTTS(text)
    tts.save("response.mp3")
    return "response.mp3"

def voice_to_text():
    """Converts voice input to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Error with speech recognition service."

# Gradio Interface
demo = gr.Interface(
    fn=ai_tutor,
    inputs=[gr.Textbox(label="Ask a Question")],
    outputs=[gr.Textbox(label="AI's Answer")],
    title="NovaTutor - AI Tutor with Learning & Live Search",
    description="Ask anything, and NovaTutor will fetch real-time information!",
)

demo.launch(server_name="0.0.0.0", server_port=7860)

