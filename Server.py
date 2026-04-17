import socket
import threading
import json
from JsonWriteRead import getDoctorList, getDoctorMonths, getMonthDays, getTimeSlots, getTodayTimeSlots, isTimeSlotAvailable, bookAppointment
from datetime import datetime

#this is a mutex lock (learned about it in operating systems). It's the tool used to stop race conditions.
bookingLock = threading.Lock()

HOST = "127.0.0.1"
PORT = 5000

temporaryDoctors = ["Jane doe", "John Doe", "Sarah Smith"]
temporaryMonths = ["April", "May", "June", "July"]
temporaryDays = [str(i) for i in range(1, 31)]
temporaryTimeSlots = ["08:00", "10:00", "12:00"]

# temporary symptom list for testing.
# later you can change the names or priorities without changing the rest of the workflow.
temporarySymptoms = [
    {"name": "Routine checkup", "priority": 1},
    {"name": "Medication refill", "priority": 1},
    {"name": "Mild cold symptoms", "priority": 2},
    {"name": "Fever", "priority": 2},
    {"name": "Persistent cough", "priority": 2},
    {"name": "Back pain", "priority": 2},
    {"name": "Vomiting", "priority": 3},
    {"name": "Difficulty breathing", "priority": 3},
    {"name": "Chest pain", "priority": 3},
    {"name": "Severe allergic reaction", "priority": 3},
]

def startServer():
    #This creates the server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #this piece of code makes restarting the server a lot easier for testing purposes.
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #binding and starting the listen for the server
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()

    print("The server is now listening")

    while True:
        #accepts clients and creates variables for them. 
        clientSocket, clientAddress = serverSocket.accept()

        #this will create the thread of the accepted client. 
        clientThread = threading.Thread(
            target=handleClient,
            args=(clientSocket, clientAddress)
        )
        clientThread.start()

def handleClient(clientSocket, clientAddress):
    session = {
        "state": "START",  #the state the client is currently in
        "selectedSymptom": None,  #memory spot for chosen symptom
        "priority": None,  #memory spot for patient's priority
        "selectedDoctor": None,  # memory spot for chosen doctor for fetch function purposes
        "selectedMonth": None,  #memory spot for chosen month for fetch function purposes
        "selectedDate": None  #memory spot for chosen day for fetch function purposes
    }
    

    try:
        while True:
            state = session["state"]

            # depending on the current state of the program, it will call that function
            if state == "START":
                startState(clientSocket, session)
            elif state == "SYMPTOM":
                chooseSymptom(clientSocket, session)
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
        # this loop takes in chunks of data until the end of the message.
        chunk = clientSocket.recv(4096)
        if not chunk:
            return None
        data += chunk

    message = data.decode().strip()
    return json.loads(message)

def startState(clientSocket, session, status="OK"):

    # determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. What would you like to do?"
    else:
        prompt = "Welcome, what would you like to do?"

    #send the info for this stage
    sendJson(clientSocket, {
        "status": status,
        "state": "START",
        "prompt": prompt,
        "options": [
            {"id": 1, "name": "Book Appointment"},
            {"id": 2, "name": "Exit"}],
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
        session["state"] = "SYMPTOM"
    elif choice == 2:
        session["state"] = "EXIT"
    else:
        startState(clientSocket, session, status="INPUT_ERROR")

def chooseSymptom(clientSocket, session, status="OK"):
    symptoms = temporarySymptoms

    #gonna take the list, and append the list to have numbers for choosing. 
    options = []
    for i, symptom in enumerate(symptoms, start=1):
        options.append({
            "id": i,
            "name": symptom["name"]
        })

    #determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose the option closest to what you are experiencing."
    else:
        prompt = "Choose the option closest to what you are experiencing."

    #send the info for this stage
    sendJson(clientSocket, {
        "status": status,
        "state": "SYMPTOM",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    # if the client doesn't respond, assume to exit for safety reasons
    if request is None:
        session["state"] = "EXIT"
        return

    #this is for if the client wants to go back a step
    if request.get("action") == "BACK":
        session["state"] = "START"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")

    if not isinstance(choice, int):
        chooseSymptom(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(symptoms):
        selected = symptoms[choice - 1]
        session["selectedSymptom"] = selected["name"]
        session["priority"] = selected["priority"]
        session["state"] = "DOCTOR"
        return

    chooseSymptom(clientSocket, session, status="INPUT_ERROR")

def chooseDoctor(clientSocket, session, status="OK"):
    #this will be where the fetch function for the list of doctors will happen, for now I use temp list
    doctors = getDoctorList()

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
    sendJson(clientSocket, {
        "status": status,
        "state": "DOCTOR",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    #if the client doesn't respond, assume to exit for safety reasons
    if request is None:
        session["state"] = "EXIT"
        return

    #this is for if the client wants to go back a step
    if request.get("action") == "BACK":
        session["state"] = "SYMPTOM"
        return

    #this makes the variable choice the client's response.
    choice = request.get("choice")

    if not isinstance(choice, int):
        chooseDoctor(clientSocket, session, status="INPUT_ERROR")
        return

    if 1 <= choice <= len(doctors):
        selected = doctors[choice - 1]
        session["selectedDoctor"] = selected

        # priority 3 patients skip month/day and go straight to today
        if session.get("priority") == 3:
            session["state"] = "TIME"
        else:
            session["state"] = "MONTH"
        return

    chooseDoctor(clientSocket, session, status="INPUT_ERROR")

def chooseMonth(clientSocket, session, status="OK"):
    #this will be where the fetch function for the list of months will happen, for now I use temp list
    months = getDoctorMonths(session["selectedDoctor"])

    #priority 1 patients must book at least a month out
    if session.get("priority") == 1:
        months = months[1:]

    #gonna take the list, and append the list to have numbers for choosing.
    options = []
    for i, month in enumerate(months, start=1):
        options.append({
            "id": i,
            "name": month
        })

    # determining prompt based off status.
    if status == "INPUT_ERROR":
        prompt = "Input invalid, try again. Choose a month to book in"
    else:
        if session.get("priority") == 1:
            prompt = "Priority 1 patient. Choose a month at least one month out."
        else:
            prompt = "Choose a month"

    #send the info for this stage
    sendJson(clientSocket, {
        "status": status,
        "state": "MONTH",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    # if the client doesn't respond, assume to exit for safety reasons
    if request is None:
        session["state"] = "EXIT"
        return

    #this is for if the client wants to go back a step
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
    #this will be where the fetch function for the list of days will happen, for now I use temp list
    days = getMonthDays(session["selectedDoctor"], session["selectedMonth"])

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
    sendJson(clientSocket, {
        "status": status,
        "state": "DAY",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    #if the client doesn't respond, assume to exit for safety reasons
    if request is None:
        session["state"] = "EXIT"
        return

    #this is for if the client wants to go back a step
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
        session["selectedDate"] = selected
        session["state"] = "TIME"
        return

    chooseDay(clientSocket, session, status="INPUT_ERROR")

def chooseTimeSlot(clientSocket, session, status="OK"):
    if session.get("priority") == 3:
        timeSlots = getTodayTimeSlots(session["selectedDoctor"])
    else:
        #this will be where the fetch function for the list of timeslots will happen, for now I use temp list
        timeSlots = getTimeSlots(session["selectedDoctor"], session["selectedMonth"], session["selectedDate"])

    #gonna take the list, and append the list to have numbers for choosing.
    options = []
    for i, slot in enumerate(timeSlots, start=1):
        options.append({
            "id": i,
            "name": slot
        })

    #determining prompt based off status.
    if status == "INPUT_ERROR":
        if session.get("priority") == 3:
            prompt = "Input invalid, try again. Priority patient, choose an appointment time for today."
        else:
            prompt = "Input invalid, try again. Choose a time slot and enter your info."
    elif status == "TAKEN":
        if session.get("priority") == 3:
            prompt = "That time slot was just taken. Priority patient, choose another appointment time for today."
        else:
            prompt = "That time slot was just taken. Choose another time slot."
    else:
        if session.get("priority") == 3:
            prompt = "Priority patient, choose an appointment time for today."
        else:
            prompt = "Choose a time slot and enter your info."

    #send the info for this stage
    sendJson(clientSocket, {
        "status": status,
        "state": "TIME",
        "prompt": prompt,
        "options": options,
        "back": True
    })

    #get response
    request = receiveJson(clientSocket)

    #if the client doesn't respond, assume to exit for safety reasons
    if request is None:
        session["state"] = "EXIT"
        return

    #this is for if the client wants to go back a step
    if request.get("action") == "BACK":
        if session.get("priority") == 3:
            session["state"] = "DOCTOR"
        else:
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

    chosenTime = timeSlots[choice - 1]

    #formating information
    bookingInfo = {
            "name": name.strip(),
            "email": email.strip(),
            "reason": reason.strip(),
            "symptom": session.get("selectedSymptom"),
            "priority": session.get("priority")
        }
    
    #setting the session's choices if priority three so that the check if the slot is still free for race condition can use.
    if session.get("priority") == 3:
        today = datetime.today()
        session["selectedMonth"] = today.strftime("%B")
        session["selectedDate"] = str(today.day)

    #the mutex lock to stop race conditions
    with bookingLock:
        #check to make sure that the appointment slot is still availab.e
        if not isTimeSlotAvailable(session["selectedDoctor"], session["selectedMonth"], session["selectedDate"], chosenTime):
            chooseTimeSlot(clientSocket, session, status="TAKEN")
            return
        
        #if the time slot isn't taken, book.
        bookAppointment(session["selectedDoctor"], session["selectedMonth"], session["selectedDate"], chosenTime, bookingInfo )
        
        

        

        #placeholder success response for now
        sendJson(clientSocket, {
            "status": "OK",
            "state": "CONFIRMATION",
            "prompt": "Appointment booked successfully.",
            "details": {
                "doctor": session["selectedDoctor"],
                "month": session["selectedMonth"],
                "day": session["selectedDate"],
                "time": chosenTime,
                "priority": session.get("priority"),
                "symptom": session.get("selectedSymptom"),
                "name": bookingInfo["name"],
                "email": bookingInfo["email"],
                "reason": bookingInfo["reason"]
            },
            "back": False
        })

        session["state"] = "EXIT"

        pass

if __name__ == "__main__":
    startServer()