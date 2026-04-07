import socket
import threading

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
        

def handleClient(scslientSocket, clientAddress):
    session = {
        "state": "START",
        "selectedDoctor": None,
        "selectedDate": None
    }

if __name__ == "__main__":
    startServer()