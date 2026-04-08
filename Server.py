import socket
import threading
import json 

#this is a mutex lock (learned about it in operating systems). It's the tool used to stop race conditions. 
bookingLock = threading.Lock()

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
    
    #this is for if the client wants to go back a step (in this case to the main menu) I made it an "action" rather than choice to avoid mistakes.
    if request.get("action") == "BACK":
        session["state"] = "START"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")
    

    if not isinstance(choice, int):
        chooseDoctor(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(doctors):
        selected = doctors[choice - 1]
        session["selectedDoctor"] = selected
        session["state"] = "MONTH"
        return

    chooseDoctor(clientSocket, session, status="INPUT_ERROR")
    

def chooseMonth(clientSocket, session, status="OK"):
    #this will be where the fetch function for the list of doctors will happen, for now I use temp list
    months = temporaryMonths

    #gonna take the list, and append the list to have numbers for choosing. 
    options = []
    for i, month in enumerate(months, start=1):
        options.append({
            "id": i,
            "name": month
        })
    


    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose a month to book in"
    else:
        prompt = "Choose a month"

    #send the info for this stage
    sendJson(clientSocket, messageFile= {
        "status": status, 
        "state": "MONTH",
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

    #this is for if the client wants to go back a step (in this case to the main menu) I made it an "action" rather than choice to avoid mistakes.
    if request.get("action") == "BACK":
        session["state"] = "DOCTOR"
        return
    
    #this makes the variable choice the client's response.
    choice = request.get("choice")
    

    if not isinstance(choice, int):
        chooseMonth(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(months):
        selected = months[choice - 1]
        session["selectedMonth"] = selected
        session["state"] = "DAY"
        return

    chooseMonth(clientSocket, session, status="INPUT_ERROR")

def chooseDay(clientSocket, session, status="OK"):
    #this will be where the fetch function for the list of doctors will happen, for now I use temp list
    days = temporaryDays

    #gonna take the list, and append the list to have numbers for choosing. 
    options = []
    for i, day in enumerate(days, start=1):
        options.append({
            "id": i,
            "name": day
        })
    


    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose a day"
    else:
        prompt = "Choose a day"

    #send the info for this stage
    sendJson(clientSocket, messageFile= {
        "status": status, 
        "state": "DAY",
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

    #this is for if the client wants to go back a step (in this case to the main menu) I made it an "action" rather than choice to avoid mistakes.
    if request.get("action") == "BACK":
        session["state"] = "MONTH"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")

    if not isinstance(choice, int):
        chooseDay(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(days):
        selected = days[choice - 1]
        session["selectedDay"] = selected
        session["state"] = "TIME"
        return

    chooseDay(clientSocket, session, status="INPUT_ERROR")

def chooseTimeSlot(clientSocket, session, status="OK"):
    #this will be where the fetch function for the list of doctors will happen, for now I use temp list
    timeSlots = temporaryTimeSlots

    #gonna take the list, and append the list to have numbers for choosing. 
    options = []
    for i, slot in enumerate(timeSlots, start=1):
        options.append({
            "id": i,
            "name": slot
        })
    


    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose a time slot and enter your info."
    elif status == "TAKEN":
        prompt = "That time slot was just taken. Choose another time slot."
    else:
        prompt = "Choose a time slot and entor your info"

    #send the info for this stage
    sendJson(clientSocket, messageFile= {
        "status": status, 
        "state": "TIME",
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

    #this is for if the client wants to go back a step (in this case to the main menu) I made it an "action" rather than choice to avoid mistakes.
    if request.get("action") == "BACK":
        session["state"] = "DAY"
        return
    
    #this makes the variable choice the client's response.
    choice = request.get("choice")

    if not isinstance(choice, int):
        chooseTimeSlot(clientSocket, session, status="INPUT_ERROR")
        return

    if not (1 <= choice <= len(timeSlots)):
        chooseTimeSlot(clientSocket, session, status="INPUT_ERROR")
        return
    
    name = request.get("name")
    email = request.get("email")
    reason = request.get("reason")

    if not isinstance(name, str) or not name.strip():
        chooseTimeSlot(clientSocket, session, status="INPUT_ERROR")
        return

    if not isinstance(email, str) or not email.strip():
        chooseTimeSlot(clientSocket, session, status="INPUT_ERROR")
        return

    if not isinstance(reason, str) or not reason.strip():
        chooseTimeSlot(clientSocket, session, status="INPUT_ERROR")
        return

    chosenTime = timeSlots[choice -1]

    with bookingLock:
        #this is where the booking of the time slot actually happens, can't do it without william's read/write functions
        #but here's the work flow:
        #check again if the chosen time slot is still available
        #if it's free call the write function that gives name, email, reason, and officially books the time slot. 
        #I think angel is doing an email confirmation function? so probably call that here as well. 

        pass



if __name__ == "__main__":
    startServer()