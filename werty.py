import csv
import os
import datetime
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import matplotlib.pyplot as plt

# --- TTS ---
def speak(text, lang='ru', filename="voice.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# --- STT ---
def recognize_speech(language='ru-RU', timeout=10):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Говорите...")
        try:
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language=language)
            print(f"🗣 Вы сказали: {text}")
            return text.lower()
        except:
            return ""

# --- INTENT DETECTION ---
intents = {
    'paid': ['оплатил', 'уже оплатил', 'платеж был', 'already paid'],
    'need_help': ['нужна помощь', 'помощь', 'help', 'support'],
    'call_back': ['перезвоните позже', 'позже', 'not now', 'call me later']
}
def detect_intent(response):
    for intent, phrases in intents.items():
        if any(p in response for p in phrases):
            return intent
    return "unknown"

# --- ASK FEATURE ---
def ask_feature(question_ru, question_en, lang='ru'):
    question = question_ru if lang == 'ru' else question_en
    speak(question, lang)
    response = recognize_speech(language='ru-RU' if lang == 'ru' else 'en-US')
    return response

# --- MAIN BOT ---
def voice_bot_dynamic(client_id=10010):
    speak("Здравствуйте, сейчас мы зададим вам несколько вопросов.", lang='ru')

    # Ask preferred language
    lang_resp = ask_feature("На каком языке вы предпочитаете общаться? Русский или Английский?",
                             "What is your preferred language? Russian or English?",
                             lang='ru')
    lang_code = 'ru' if 'рус' in lang_resp or lang_resp == '' else 'en'
    recog_lang = 'ru-RU' if lang_code == 'ru' else 'en-US'

    # Ask features in preferred language
    age_resp = ask_feature("Сколько вам лет?", "How old are you?", lang=lang_code)
    channel_resp = ask_feature("Вы используете мобильный или стационарный телефон?",
                               "Are you using a mobile or landline phone?", lang=lang_code)
    notif_resp = ask_feature("Вас беспокоит задолженность или информация о тарифах?",
                             "Are you being contacted about debt or tariffs?", lang=lang_code)

    # Confirm call time
    current_time = datetime.datetime.now().strftime('%H:%M')
    call_time_check = ask_feature(f"Сейчас {current_time}. Это удобное время для звонка?",
                                  f"It’s {current_time} now. Is this a good time to talk?",
                                  lang=lang_code)

    # Ask about history
    history_resp = ask_feature("Мы уже связывались с вами ранее. Вы это помните?",
                               "We contacted you before. Do you remember?",
                               lang=lang_code)

    client = {
        'id': client_id,
        'age': age_resp,
        'language': lang_code,
        'notification': 'debt' if 'долг' in notif_resp or 'debt' in notif_resp else 'tariff',
        'channel': 'mobile' if 'моб' in channel_resp or 'mobile' in channel_resp else 'landline',
        'call_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'history_confirmation': history_resp,
        'response': ''
    }

    # Call scenario
    speak("Спасибо, начинаю звонок.", lang=lang_code)
    speak("Здравствуйте, это ваш банк.", lang=lang_code)

    if client['notification'] == 'debt':
        speak("У вас есть задолженность. Вы оплатили?" if lang_code == 'ru' else "You have a payment due. Have you paid?", lang=lang_code)
    else:
        speak("У нас обновились тарифы. Хотите узнать?" if lang_code == 'ru' else "We have updated tariffs. Would you like more info?", lang=lang_code)

    # Listen and detect
    response = recognize_speech(language=recog_lang)
    intent = detect_intent(response)

    # Respond
    if intent == 'paid':
        speak("Спасибо за оплату." if lang_code == 'ru' else "Thanks for the payment.", lang=lang_code)
        result, comment = "success", "confirmed payment"
    elif intent == 'need_help':
        speak("Оператор свяжется с вами." if lang_code == 'ru' else "Representative will contact you.", lang=lang_code)
        result, comment = "success", "asked for help"
    elif intent == 'call_back':
        speak("Мы перезвоним позже." if lang_code == 'ru' else "We’ll call you later.", lang=lang_code)
        result, comment = "fail", "call back requested"
    elif response == "":
        speak("Нет ответа. Перезвоним позже." if lang_code == 'ru' else "No response. Will call back.", lang=lang_code)
        result, comment = "fail", "no response"
    else:
        speak("Спасибо. До свидания!" if lang_code == 'ru' else "Thank you. Goodbye!", lang=lang_code)
        result, comment = "success", "info received"

    log = {
        "client_id": client['id'],
        "age": client['age'],
        "language": client['language'],
        "channel": client['channel'],
        "notification": client['notification'],
        "call_time": client['call_time'],
        "history_confirmation": client['history_confirmation'],
        "response": response,
        "result": result,
        "comment": comment
    }

    save_to_csv(log)
    return log

# --- SAVE TO CSV ---
def save_to_csv(log, file_path="call_logs.csv"):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['client_id', 'age', 'language', 'channel', 'notification',
                      'call_time', 'history_confirmation', 'response', 'result', 'comment']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log)

# --- VISUALIZATION ---
def visualize_call_history(file_path="call_logs.csv"):
    if not os.path.isfile(file_path):
        print("📁 Логов нет.")
        return
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        logs = list(reader)

    success = sum(1 for log in logs if log['result'] == 'success')
    fail = sum(1 for log in logs if log['result'] == 'fail')
    unknown = len(logs) - success - fail

    labels = ['Success', 'Fail', 'Other']
    sizes = [success, fail, unknown]
    colors = ['green', 'red', 'gray']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=140)
    plt.title('📊 Call Outcomes')
    plt.axis('equal')
    plt.show()

# === RUN BOT ===
log = voice_bot_dynamic()
print("\n📤 ИТОГ:", f"{log['client_id']}|{log['result']}|{log['comment']}")
visualize_call_history()