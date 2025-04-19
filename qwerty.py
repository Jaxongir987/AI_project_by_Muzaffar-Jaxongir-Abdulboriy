import pyttsx3
import speech_recognition as sr
import datetime

# Initialize TTS engine
engine = pyttsx3.init()

# Speak function
def speak(text):
    print(f"🤖 Bot: {text}")
    engine.say(text)
    engine.runAndWait()

# Listen function
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)
    try:
        response = r.recognize_google(audio)
        print(f"🗣️ User: {response}")
        return response.lower()
    except:
        speak("I didn't catch that. Can you repeat?")
        return ""

# AI Logic (simple NLP rules)
def ai_brain(text):
    if "hello" in text or "hi" in text:
        return "Hello! How can I help you today?"
    elif "your name" in text:
        return "I'm your virtual assistant."
    elif "time" in text:
        now = datetime.datetime.now().strftime("%H:%M")
        return f"The current time is {now}."
    elif "debt" in text or "payment" in text:
        return "You have an unpaid bill due on April 25th."
    elif "bye" in text:
        return "Goodbye! Have a nice day."
    else:
        return "Sorry, I don't understand that yet."

# Main loop
def voice_bot():
    speak("Hello! This is your voice assistant.")
    while True:
        query = listen()
        if query:
            answer = ai_brain(query)
            speak(answer)
            if "bye" in query:
                break

# Start the bot
voice_bot()
