import socket
import pyttsx3
import json

HOST = "127.0.0.1"
PORT = 5000

#THIS IS NOT DONE!!!!!!!!

#This is a function used for sending json files to the client
def sendJson(clientSocket, messageFile):
    message = json.dumps(messageFile) + "\n"
    clientSocket.sendall(message.encode())

#and this function is for receiving messages
def receiveJson(clientSocket):
    data = b""

    while b"\n" not in data:
        # this loop takes in chunks of data until the end of the message.
        chunk = clientSocket.recv(4096)
        if not chunk:
            return None
        data += chunk

    message = data.decode().strip()
    return json.loads(message)


def handleUser():
    #boolean statement for if client wants TTS or not. 
    ttsToggle = True

    #checks to see if user wants TTS.
    while True:
        print("Do you wish to use text to speech? type 1 for yes, 2 for no.")
        speak("Do you wish to use text to speech? type 1 for yes, 2 for no.")
        x = input()
        if x == "1":
            break
        elif x == "2":
            ttsToggle = False
            break
        else:
            print("Not a valid input.")
            speak("Not a valid input.")




    #creates client socket, and connects to server. 
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((HOST, PORT))

    #general workflow loop. 
    while(True):
        serverResponse = receiveJson(clientSocket)
        print(serverResponse.get("prompt"))
        for option in serverResponse["options"]:
            print(f'{option["id"]}. {option["name"]}')

        if ttsToggle:
            while True:
                speak(serverResponse.get("prompt"))
                for option in serverResponse["options"]:
                    speak(f'{option["id"]}. {option["name"]}')
                speak("if you wish to repeat? enter tilda if yes")
                x = input()
                if x == "`" or "~":
                    continue
                

        


        
        
            
    
    
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    handleUser()


