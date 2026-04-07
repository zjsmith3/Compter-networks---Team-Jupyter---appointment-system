import socket
import threading
import json 

HOST = "127.0.0.1"
PORT = 5000

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

def startState(clientSocket, session):
    print("temp")


def chooseDoctor(clientSocket, session):
    print("temp")


def chooseMonth(clientSocket, session):
    print("temp")


def chooseDay(clientSocket, session):
    print("temp")


def chooseTimeSlot(clientSocket, session):
    print("temp")





if __name__ == "__main__":
    startServer()