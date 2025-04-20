import pyttsx3
import speech_recognition as sr
import datetime
import os

# === Init TTS Engine with male voice ===
tts_engine = pyttsx3.init()
voices = tts_engine.getProperty('voices')
for voice in voices:
    if "male" in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break

# === Phrase templates ===
phrases = {
    "en": {
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
    },
    "ru": {
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
}

# === Save all phrases as MP3 files ===
def generate_mp3_files():
    os.makedirs("sounds_en", exist_ok=True)
    os.makedirs("sounds_ru", exist_ok=True)
    for lang, group in phrases.items():
        for key, text in group.items():
            filepath = f"sounds_{lang}/{key}.mp3"
            if not os.path.exists(filepath):
                print(f"Generating: {filepath}")
                tts_engine.save_to_file(text, filepath)
    tts_engine.runAndWait()
generate_mp3_files()

# === Speak using pre-saved audio ===
def speak(text, lang="en"):
    print("Bot:", text)
    key = next((k for k, v in phrases[lang].items() if v == text), None)
    if key:
        filepath = f"sounds_{lang}/{key}.mp3"
        if os.path.exists(filepath):
            os.system(f"start {filepath}" if os.name == 'nt' else f"afplay '{filepath}'" if os.name == 'posix' else f"xdg-open '{filepath}'")
        else:
            # fallback in case file is missing
            tts_engine.say(text)
            tts_engine.runAndWait()
    else:
        # fallback for custom dynamic texts
        tts_engine.say(text)
        tts_engine.runAndWait()

# === Listen with retry ===
def listen(language="en-US", retries=2):
    recognizer = sr.Recognizer()
    for _ in range(retries):
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        try:
            response = recognizer.recognize_google(audio, language=language)
            print("User:", response)
            return response.lower()
        except sr.UnknownValueError:
            speak(phrases['en' if language == 'en-US' else 'ru']["reask"], 'en' if language == 'en-US' else 'ru')
        except sr.RequestError:
            speak("Service error. Try again later.", 'en' if language == 'en-US' else 'ru')
            return "error"
    return "unknown"

# === Main logic ===
def make_call(client_id):
    speak("Здравствуйте! / Hello! This is a call from your bank.", "en")

    speak("Please say your preferred language: English or Russian.", "en")
    lang_response = listen(language="en-US")

    if "russian" in lang_response or "рус" in lang_response:
        lang = "ru"
        voice_code = "ru-RU"
    else:
        lang = "en"
        voice_code = "en-US"

    t = phrases[lang]

    speak(t["greet"], lang)
    speak(t["debt"], lang)
    response = listen(voice_code)

    if "yes" in response or "да" in response:
        result = "success"
        payment_status = "paid"
    elif "no" in response or "нет" in response or "not yet" in response:
        result = "success"
        payment_status = "not paid"
    elif "call back" in response or "перезвони" in response:
        speak(t["callback"], lang)
        return {"client_id": client_id, "result": "fail", "comment": "asked for callback"}
    elif response in ["unknown", "error"]:
        return {"client_id": client_id, "result": "fail", "comment": "unreachable"}
    else:
        result = "success"
        payment_status = "response unclear"

    speak(t["help"], lang)
    listen(voice_code)

    speak(t["tariff"], lang)

    speak(t["ask_name"], lang)
    name = listen(voice_code)

    speak(t["ask_age"], lang)
    age = listen(voice_code)

    speak(t["ask_notify"], lang)
    notification = listen(voice_code)

    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"{t['call_time']}{time_now}", lang)

    speak(t["comm_type"], lang)
    comm = listen(voice_code)

    speak(t["history"], lang)
    speak(t["thanks"], lang)
    speak(t["goodbye"], lang)

    return {
        "client_id": client_id,
        "result": result,
        "comment": f"payment_status: {payment_status}\n"
                   f"name: {name}\n"
                   f"age: {age}\n"
                   f"notify: {notification}\n"
                   f"comm: {comm}"
    }

# === Print result nicely ===
def log_result(result_dict):
    print("\nCall Summary:")
    print("client_id | result     | comment")
    print("------------------------------------------")
    print(f"{result_dict['client_id']}        | {result_dict['result']} | \n{result_dict['comment']}")

# === Run call ===
call_result = make_call(10001)
log_result(call_result)
