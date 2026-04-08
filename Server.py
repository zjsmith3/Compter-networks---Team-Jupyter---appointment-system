import socket
import threading
import json 

HOST = "127.0.0.1"
PORT = 5000

temporaryDoctors = ["Jane doe", "John Doe", "Sarah Smith"]
temporaryMonths = ["May", "June", "July"]
temporaryDays = ["1", "2", "3", "4", "5"]
temporaryTimeSlots = ["08:00", "10:00", "12:00"]

def startServer():
    #creatign the server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #this piece of code makes restarting the server easier for testing purposes. 
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #binding and starting the listen. 
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()

    print(f"The server is now listening")

    while True:
    #creating a variable that is the client upon an acceptance.
        clientSocket, clientAddress = serverSocket.accept()

        #this creates a thread that essentially runs the server 
        clientThread = threading.Thread(
            target=handleClient,
            args=(clientSocket, clientAddress)
        )
        

def handleClient(clientSocket, clientAddress):
    session = {
        "state": "START",  #the state the client is currently in
        "selectedDoctor": None,  #memory spot for chosen doctor for fetch function purposes
        "selectedMonth": None,  #memory spot for chosen month for fetch function purposes
        "selectedDate": None #memory spot for chosen date for fetch function purposes
    }

    try:
        while True:
            state = session["state"]

            #depending on the current state of the program, it will call that function
            if state == "START":
                startState(clientSocket, session)
            elif state == "DOCTOR":
                chooseDoctor(clientSocket, session)
            elif state == "MONTH":
                chooseMonth(clientSocket, session)
            elif state == "DAY":
                chooseDay(clientSocket, session)
            elif state == "TIME":
                chooseTimeSlot(clientSocket, session)
            elif state == "EXIT":
                break
            else:
                break
    
    finally:
        clientSocket.close()


#This is a function used for sending json files to the client
def sendJson(clientSocket, messageFile):
    message = json.dumps(messageFile) + "\n"
    clientSocket.sendall(message.encode())
#and this function is for receiving messages

def receiveJson(clientSocket):
    data = b""

    while b"\n" not in data:
        #this loop takes in chunks of data untill the end of the message. 
        chunk = clientSocket.recv(4096)
        if not chunk:
            return None
        data += chunk
    
    message = data.decode().strip()
    return json.loads(message)

def startState(clientSocket, session, status="OK"):

    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. What would you like to do?"
    else:
        prompt = "Welcome, what would you like to do?"

    #send the info for this stage
    sendJson(clientSocket, messageFile= {
        "status": status, 
        "state": "START",
        "prompt": prompt,
        "options": {1: "Book Appointment", 2: "Exit"},
        "back": False
    })

    #get response
    request = receiveJson(clientSocket)

    #if the client doesn't respond, assume to exit for safety reasons
    if request == None:
        session["state"] = "EXIT"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")

    if choice == 1:
        session["state"] = "DOCTOR"
    elif choice == 2:
        session["state"] = "EXIT"
    else:
        startState(clientSocket, session, status="INPUT_ERROR")

def chooseDoctor(clientSocket, session, status="OK"):
   
    #this will be where the fetch function for the list of doctors will happen, for now I use temp list
    doctors = temporaryDoctors

    #gonna take the list, and append the list to have numbers for choosing. 
    options = []
    for i, doctor in enumerate(doctors, start=1):
        options.append({
            "id": i,
            "name": doctor
        })
    


    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose a doctor"
    else:
        prompt = "Choose a doctor"

    #send the info for this stage
    sendJson(clientSocket, messageFile= {
        "status": status, 
        "state": "DOCTOR",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    #if the client doesn't respond, assume to exit for safety reasons
    if request == None:
        session["state"] = "EXIT"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")
    
    #this is for if the client wants to go back a step (in this case to the main menu) I made it an "action" rather than choice to avoid mistakes.
    if request.get("action") == "BACK":
        session["state"] = "START"
        return

    if not isinstance(choice, int):
        chooseDoctor(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(doctors):
        selected = doctors[choice - 1]
        session["selectedDoctor"] = selected
        session["state"] = "MONTH"
        return

    chooseDoctor(clientSocket, session, status="INPUT_ERROR")
    

def chooseMonth(clientSocket, session):
    print("temp")

def chooseDay(clientSocket, session):
    print("temp")

def chooseTimeSlot(clientSocket, session):
    print("temp")





if __name__ == "__main__":
    startServer()