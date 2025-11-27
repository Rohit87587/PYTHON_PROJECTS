import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS
from google import genai
import pygame
from dotenv import load_dotenv
import os
from datetime import datetime
import pywhatkit
import pyautogui

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=GENAI_API_KEY)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Speak function using gTTS and pygame

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")

# AI Processing function using Google Gemini API

def aiProcess(command):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  
            contents=f"User said: {command}. Reply as Jarvis:"
        )

        # return only text
        return response.text

    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I am unable to process that."
         

def processCommand(c):

    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif c.lower().startswith("play"):
        song = c.lower().replace("play", "").strip()

        if song in musicLibrary.music:
            speak(f"Playing {song}")
            webbrowser.open(musicLibrary.music[song])
        else:
            speak(f"Playing {song} on YouTube")
            pywhatkit.playonyt(song)

    elif "news" in c:
        try:
            url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&apikey={NEWS_API_KEY}"
            r = requests.get(url)

            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])

                if not articles:
                    speak("No news found.")
                else:
                    for article in articles[:5]:
                        speak(article["title"])
            else:
                speak("Unable to fetch news right now.")

        except Exception as e:
            print(e)
            speak("Error fetching news.")

    elif "weather" in c.lower():
        city = "Morbi"
        if "in" in c.lower():
            city = c.lower().split("in")[-1].strip()

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                speak(f"The temperature in {city} is {temp} degrees Celsius with {desc}")
            else:
                speak(f"I could not find the weather for {city}")

        except Exception as e:
            speak("Error fetching weather")

    elif "time" in c.lower():
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    # ... previous code ...

    elif "screenshot" in c.lower():

        speak("Taking a screenshot, sir.")
        
        # Takes a screenshot and saves it with a unique name
        im = pyautogui.screenshot()
        im.save("screenshot.png") 
        speak("Screenshot saved.")

    elif "volume up" in c.lower():
        pyautogui.press("volumeup")
        pyautogui.press("volumeup")
        speak("Volume increased")

    elif "volume down" in c.lower():
        pyautogui.press("volumedown")
        pyautogui.press("volumedown")
        speak("Volume decreased")
        
    elif "mute" in c.lower():
        pyautogui.press("volumemute")
        speak("System muted")

    else:
        output = aiProcess(c)
        speak(output)

# Main loop to listen for wake word and process commands

if __name__ == "__main__":
    speak("Initializing Jarvis...")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=1)

            word = recognizer.recognize_google(audio).lower()

            if word == "jarvis":
                speak("Yes?")
                print("Jarvis activated...")

                with sr.Microphone() as source:
                    audio = recognizer.listen(source)

                command = recognizer.recognize_google(audio)
                print("Command:", command)

                processCommand(command)

        except Exception as e:
            print("Error:", e)



