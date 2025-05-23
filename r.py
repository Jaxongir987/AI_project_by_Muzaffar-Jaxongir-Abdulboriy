import pyttsx3
import speech_recognition as sr
import datetime
import sqlite3

# Init TTS engine with male voice
tts_engine = pyttsx3.init()
voices = tts_engine.getProperty('voices')
for voice in voices:
    if "male" in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break

# Speak
def speak(text):
    print("Bot:", text)
    tts_engine.say(text)
    tts_engine.runAndWait()

# Listen (with retry if unknown)
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
            speak("I didn't catch that. Please repeat.")
        except sr.RequestError:
            speak("Service error. Try again later.")
            return "error"
    return "unknown"

# Main call logic
def make_call(client_id):
    speak("Здравствуйте! Hello! Salom! This is a call from your bank.")
    speak("Please say your preferred language: English, Russian or Uzbek.")

    lang_response = listen(language="en-US")
    if "russian" in lang_response or "рус" in lang_response:
        lang = "ru-RU"
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
    elif "uzbek" in lang_response or "o'zbek" in lang_response or "uzbekcha" in lang_response:
        lang = "uz-UZ"
        t = {
            "greet": "Salom! Bu sizning bankingizdan qo'ng'iroq.",
            "debt": "Sizda hisob bo'yicha qarz bor. To'lov muddati ertaga. Siz allaqachon to'lov qildingizmi?",
            "reask": "Kechirasiz, tushunmadim. Iltimos, yana ayting.",
            "help": "Yordam kerakmi? Sizni operator bilan ulayman.",
            "callback": "Yaxshi, keyinroq yana qo'ng'iroq qilaman. Xayr.",
            "tariff": "Ma'lumot uchun: tariflar o'zgardi. Xizmat haqi 10 foizga oshirildi.",
            "ask_name": "Ismingiz nima?",
            "ask_age": "Yoshingiz nechida?",
            "ask_notify": "Bildirishnomalarni qanday olishni xohlaysiz? Masalan, SMS yoki qo'ng'iroq orqali?",
            "call_time": "Qo'ng'iroq vaqti: ",
            "comm_type": "Siz qanday aloqa turidan foydalanasiz: mobil yoki statsionar telefon?",
            "history": "Sizning oxirgi murojaatingiz 2 hafta oldin kredit karta haqida bo‘lgan.",
            "thanks": "Ma'lumot uchun rahmat.",
            "goodbye": "Xayr!"
        }
    else:
        lang = "en-US"
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

    speak(t["greet"])

    # Ask about payment
    speak(t["debt"])
    response = listen(lang)
    if "yes" in response or "ha" in response or "да" in response:
        result = "success"
        comment = "confirmed payment"
    elif "no" in response or "yo'q" in response or "нет" in response or "not yet" in response:
        result = "success"
        comment = "needs help or follow-up"
    elif "call back" in response or "перезвони" in response or "qayta" in response:
        speak(t["callback"])
        return {"client_id": client_id, "result": "fail", "comment": "asked for callback"}
    elif response in ["unknown", "error"]:
        result = "fail"
        comment = "unreachable"
    else:
        result = "success"
        comment = "received info"

    # Ask if customer needs help
    speak(t["help"])
    listen(lang)

    # Share tariff info
    speak(t["tariff"])

    # Collect info
    speak(t["ask_name"])
    name = listen(lang)

    speak(t["ask_age"])
    age = listen(lang)

    speak(t["ask_notify"])
    notification = listen(lang)

    # Say call time
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"{t['call_time']}{time_now}")

    # Communication type
    speak(t["comm_type"])
    comm = listen(lang)

    # History
    speak(t["history"])

    speak(t["thanks"])
    speak(t["goodbye"])

    return {
        "client_id": client_id,
        "result": result,
        "comment": f"{comment}; name: {name}, age: {age}, notify: {notification}, comm: {comm}"
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
