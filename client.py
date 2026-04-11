import socket
import pyttsx3



def handleUser():
    print("temp")
    speak("test test test test")
    
def speak(text):
    engine = pyttsx3.init()

    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    handleUser()
