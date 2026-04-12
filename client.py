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

def handleBack(clientSocket):
    print("temp")

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
        #PRINTING
        #get the server's message
        serverResponse = receiveJson(clientSocket)

        if serverResponse.get("state") == "CONFIRMATION":
            print(serverResponse.get("prompt"))
            if ttsToggle:
                speak(serverResponse.get("prompt"))
            break


        while True:

            #print's the server message
            print(serverResponse.get("prompt"))
            #print the options available. 
            for option in serverResponse["options"]:
                print(f'{option["id"]}. {option["name"]}')
            #if back is enabled:
            if serverResponse["back"] == True:
                print("0. go back")
            #if tts is on print:
            if ttsToggle == True:
                print("do you wish to repeat prompt? enter tilda if yes")
        
            #if text to speak is on, use this workflow. 

            if ttsToggle:
            #TTS
                #speaks the server resopnse
                speak(serverResponse.get("prompt"))
            #speak each option
                for option in serverResponse["options"]:
                    speak(f'{option["id"]}. {option["name"]}')
                if serverResponse["back"] == True:
                    speak("0. go back")
            #add to the response, saying to enter tilda if you want the message to repeat
                speak("do you wish to repeat prompt? enter tilda if yes")

            userInput = input()
                #if input is tilda, repeat the prompt and options. 
            if userInput == "`" or userInput == "~":
                continue
                
            if userInput == "0":
                if serverResponse["back"] == True:
                    sendJson(clientSocket, {
                        "action": "BACK"
                    })
                    break
                else:
                    print("Back is not allowed in this menu")
                    if ttsToggle:
                        speak("Back is not allowed in this menu")
            else:
                try:
                    userInput = int(userInput)
                except ValueError:
                    print("Answer was not an integer, please try again.")
                    if ttsToggle:
                        speak("Answer was not an integer, please try again.")
                    continue

                if serverResponse.get("state") == "TIME":
                    print("Enter your name")
                    if ttsToggle:
                        speak("Enter your name")
                    name = input()

                    print("Enter your email")
                    if ttsToggle:
                        speak("Enter your email")
                    email = input()

                    print("Enter the reason for your appointment")
                    if ttsToggle:
                        speak("Enter the reason for your appointment")
                    reason = input()

                    sendJson(clientSocket, {
                        "choice": userInput,
                        "name": name,
                        "email": email,
                        "reason": reason
                    })
                else:
                    sendJson(clientSocket, {
                        "choice": userInput
                    })

                break
            
            



                #if input 

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    handleUser()


