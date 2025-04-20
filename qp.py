import os
import time
import datetime
import speech_recognition as sr
from TTS.api import TTS
from IPython.display import display, HTML

# Initialize TTS model (multilingual + multi-speaker)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

# Get available speakers from the model
available_speakers = tts.speakers
speaker_map = {
    "en": available_speakers[0],  # English speaker
    "ru": available_speakers[1]   # Russian speaker
}

# Play audio in Jupyter Notebook
def display_and_play_audio(file_path="output.wav"):
    display(HTML(f"""
        <audio autoplay>
            <source src="{file_path}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    """))

# Speak using TTS + WAV
def speak(text, lang="en"):
    speaker = speaker_map.get(lang, available_speakers[0])
    print("Bot:", text)
    tts.tts_to_file(text=text, speaker=speaker, language=lang, file_path="output.wav")
    display_and_play_audio("output.wav")
    time.sleep(1.5)

# Listen to user
def listen(language="en-US", retries=2):
    recognizer = sr.Recognizer()
    for _ in range(retries):
        with sr.Microphone() as source:
            print("🎤 Listening...")
            audio = recognizer.listen(source)
        try:
            response = recognizer.recognize_google(audio, language=language)
            print("User:", response)
            return response.lower()
        except sr.UnknownValueError:
            speak("I didn't catch that. Please repeat.", lang=language[:2])
        except sr.RequestError:
            speak("Service error. Try again later.", lang=language[:2])
            return "error"
    return "unknown"

# Call logic
def make_call(client_id):
    speak("Здравствуйте! Hello! This is a call from your bank.", lang="en")
    speak("Please say your preferred language: English or Russian.", lang="en")
    lang_response = listen("en-US")

    if "russian" in lang_response or "рус" in lang_response:
        lang_code = "ru"
        recog_lang = "ru-RU"
        t = {
            "greet": "Здравствуйте! Это звонок из вашего банка.",
            "debt": "У вас есть задолженность по счету. Крайний срок оплаты — завтра. Вы уже оплатили?",
            "reask": "Я не расслышал. Повторите, пожалуйста.",
            "help": "Вам нужна помощь? Я могу соединить вас с оператором.",
            "callback": "Хорошо, я перезвоню позже. До свидания.",
            "tariff": "К вашему сведению: тарифы были изменены. Плата за обслуживание увеличена на 10 процентов.",
            "ask_name": "Как вас зовут?",
            "ask_age": "Сколько вам лет?",
            "ask_notify": "Как вы хотите получать уведомления? Например, по СМС или звонку?",
            "call_time": "Время звонка: ",
            "comm_type": "Какой тип связи вы используете: мобильный или стационарный телефон?",
            "history": "Ваш последний контакт с банком был 2 недели назад по поводу кредитной карты.",
            "thanks": "Спасибо за информацию.",
            "goodbye": "До свидания!"
        }
    else:
        lang_code = "en"
        recog_lang = "en-US"
        t = {
            "greet": "Hello! This is a call from your bank.",
            "debt": "You have an outstanding bill. The payment deadline is tomorrow. Have you already paid?",
            "reask": "I didn't catch that. Could you please repeat?",
            "help": "Do you need help? I can connect you to our support center.",
            "callback": "Okay, I will call you back later. Goodbye.",
            "tariff": "Just to inform you: the tariffs have changed. Service charges increased by 10 percent.",
            "ask_name": "May I know your name?",
            "ask_age": "How old are you?",
            "ask_notify": "How would you like to receive notifications? For example, via SMS or call?",
            "call_time": "Call time: ",
            "comm_type": "What type of phone connection do you use — mobile or landline?",
            "history": "Your last interaction was 2 weeks ago regarding a credit card issue.",
            "thanks": "Thank you for the information.",
            "goodbye": "Goodbye!"
        }

    speak(t["greet"], lang=lang_code)

    speak(t["debt"], lang=lang_code)
    response = listen(recog_lang)

    if "yes" in response or "да" in response:
        result = "success"
        comment = "confirmed payment"
    elif "no" in response or "нет" in response or "not yet" in response:
        result = "success"
        comment = "needs help or follow-up"
    elif "call back" in response or "перезвони" in response:
        speak(t["callback"], lang=lang_code)
        return {"client_id": client_id, "result": "fail", "comment": "asked for callback"}
    elif response in ["unknown", "error"]:
        result = "fail"
        comment = "unreachable"
    else:
        result = "success"
        comment = "received info"

    speak(t["help"], lang=lang_code)
    listen(recog_lang)

    speak(t["tariff"], lang=lang_code)

    speak(t["ask_name"], lang=lang_code)
    name = listen(recog_lang)

    speak(t["ask_age"], lang=lang_code)
    age = listen(recog_lang)

    speak(t["ask_notify"], lang=lang_code)
    notify = listen(recog_lang)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"{t['call_time']}{now}", lang=lang_code)

    speak(t["comm_type"], lang=lang_code)
    comm = listen(recog_lang)

    speak(t["history"], lang=lang_code)
    speak(t["thanks"], lang=lang_code)
    speak(t["goodbye"], lang=lang_code)

    return {
        "client_id": client_id,
        "result": result,
        "comment": f"{comment}; name: {name}, age: {age}, notify: {notify}, comm: {comm}"
    }

# Log result
def log_result(result):
    print("\n📞 Call Summary:")
    print("client_id | result     | comment")
    print("----------------------------------------------")
    print(f"{result['client_id']}        | {result['result']} | {result['comment']}")

# Run call
call_result = make_call(10001)
log_result(call_result)
