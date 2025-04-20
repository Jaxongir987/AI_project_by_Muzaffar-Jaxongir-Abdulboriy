from TTS.api import TTS
import speech_recognition as sr
import datetime
import time
import os

# Initialize Coqui TTS with a multilingual model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

# Speak function using TTS (with language handling)
def speak(text, lang="en"):
    print("Bot:", text)
    # Specify the correct language for the speaker
    tts.tts_to_file(text=text, speaker=lang, file_path="output.wav")
    os.system("start output.wav" if os.name == "nt" else "afplay output.wav" if os.name == "posix" else "aplay output.wav")

# Listen function with retries
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
            speak("I didn't catch that. Please repeat.", lang=language[:2])
        except sr.RequestError:
            speak("Service error. Try again later.", lang=language[:2])
            return "error"
    return "unknown"

# Main call logic
def make_call(client_id):
    speak("Здравствуйте!  Hello! This is a call from your bank.", lang="en")

    speak("Please say your preferred language: English or Russian.", lang="en")
    lang_response = listen(language="en-US")

    if "russian" in lang_response or "рус" in lang_response:
        lang = "ru-RU"
        short_lang = "ru"
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
        lang = "en-US"
        short_lang = "en"
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

    speak(t["greet"], lang=short_lang)

    speak(t["debt"], lang=short_lang)
    response = listen(lang)

    if "yes" in response or "да" in response:
        result = "success"
        comment = "confirmed payment"
    elif "no" in response or "нет" in response or "not yet" in response:
        result = "success"
        comment = "needs help or follow-up"
    elif "call back" in response or "перезвони" in response:
        speak(t["callback"], lang=short_lang)
        return {"client_id": client_id, "result": "fail", "comment": "asked for callback"}
    elif response in ["unknown", "error"]:
        result = "fail"
        comment = "unreachable"
    else:
        result = "success"
        comment = "received info"

    speak(t["help"], lang=short_lang)
    help_response = listen(lang)

    if any(phrase in help_response for phrase in ["yes", "i need help", "да", "нужна помощь", "помоги"]):
        time.sleep(5)

    speak(t["tariff"], lang=short_lang)

    speak(t["ask_name"], lang=short_lang)
    name = listen(lang)

    speak(t["ask_age"], lang=short_lang)
    age = listen(lang)

    speak(t["ask_notify"], lang=short_lang)
    notification = listen(lang)

    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"{t['call_time']}{time_now}", lang=short_lang)

    speak(t["comm_type"], lang=short_lang)
    comm = listen(lang)

    speak(t["history"], lang=short_lang)

    speak(t["thanks"], lang=short_lang)
    speak(t["goodbye"], lang=short_lang)

    return {
        "client_id": client_id,
        "result": result,
        "comment": f"{comment}\n"
                   f"name: {name}\n"
                   f"age: {age}\n"
                   f"notify: {notification}\n"
                   f"comm: {comm}"
    }

# Log result in table format
def log_result(result_dict):
    print("\n📞 Call Summary:")
    print("client_id | result     | comment")
    print("----------------------------------------------")
    print(f"{result_dict['client_id']}        | {result_dict['result']} | {result_dict['comment']}")

# Example call
call_result = make_call(10001)
log_result(call_result)
