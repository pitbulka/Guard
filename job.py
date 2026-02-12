import os
import json
import queue
import ssl
import requests
import sounddevice as sd
import vosk
import pyttsx3
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)
ssl._create_default_https_context = ssl._create_unverified_context

GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MODEL_PATH = "model"
MEMORY_FILE = "memory.json"
SMART_FILE = "smart_memory.json"
WAKE_WORD = "страж"

engine = pyttsx3.init()
engine.setProperty("rate", 175)

def speak(text):
    print(Fore.MAGENTA + f"\n🤖 Страж: {text}\n")
    engine.say(text)
    engine.runAndWait()

def load_memory(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

memory = load_memory(MEMORY_FILE)
smart_memory = load_memory(SMART_FILE)

def save_memory_file(file, mem):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def get_time_date():
    now = datetime.now()
    return f"Сейчас {now.strftime('%H:%M')}, {now.strftime('%d.%m.%Y')}"

def get_weather(city="москва"):
    if not WEATHER_API_KEY:
        return "Ключ погоды не задан."
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "ru"},
        timeout=10
    )
    data = r.json()
    return f"{city.capitalize()}: {data['main']['temp']}°C, {data['weather'][0]['description']}"

def smart_learn(command, response):
    if command.lower() not in smart_memory:
        smart_memory[command.lower()] = response
        save_memory_file(SMART_FILE, smart_memory)

def smart_advice(text):
    t = text.lower()
    if "рецепт" in t or "готовить" in t:
        return "Могу подсказать рецепты на любой вкус: от пиццы до суши."
    if "здоровье" in t:
        return "Регулярные прогулки и питьё воды — основа здоровья."
    if "диета" in t:
        return "Для диеты лучше есть больше овощей, белка и меньше сахара."
    return None

q = queue.Queue()
model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())["text"]
                if text:
                    return text

def handle(command):
    t = command.lower()
    if "время" in t or "дата" in t:
        return get_time_date()
    advice = smart_advice(t)
    if advice:
        smart_learn(command, advice)
        return advice
    return "Я пока не знаю, как на это ответить."

def main():
    speak("Страж активен. Ожидаю команду.")
    while True:
        text = listen()
        print(Fore.GREEN + "Вы:", text)
        if WAKE_WORD in text.lower():
            speak("Да, сэр. Что приказываете?")
            command = listen()
            print(Fore.CYAN + "Команда:", command)
            result = handle(command)
            memory[command.lower()] = result
            save_memory_file(MEMORY_FILE, memory)
            speak(result)

if __name__ == "__main__":
    main()
