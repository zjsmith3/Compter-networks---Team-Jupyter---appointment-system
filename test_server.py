import socket
import json

HOST = "127.0.0.1"
PORT = 5000

def send_and_receive(sock, message):
    # send a message to the server and wait for reply
    sock.sendall((json.dumps(message) + "\n").encode()) #convert dictionary to json string, add newline then send
    data = sock.recv(4096).decode().strip()  # get response from server
    return json.loads(data)  # turn it back into a dictionary


def test_start_menu():
    # connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # server should send the START menu right away
    data = sock.recv(4096).decode().strip()
    response = json.loads(data)

    # check if we are really in START state
    assert response["state"] == "START"

    # make sure menu options exist
    assert "options" in response

    sock.close()


def test_start_to_symptom():
    # connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.recv(4096)  # ignore the first START message

    # choose option 1 (Book Appointment)
    res = send_and_receive(sock, {"choice": 1})

    # should move to SYMPTOM screen
    assert res["state"] == "SYMPTOM"

    sock.close()


def test_invalid_menu_input():
    # connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.recv(4096)  # get START menu

    # send something wrong (string instead of number)
    res = send_and_receive(sock, {"choice": "abc"})

    # server should catch the error
    assert res["status"] == "INPUT_ERROR"

    sock.close()


def test_back_navigation():
    # connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.recv(4096)  # START menu

    # go forward first
    send_and_receive(sock, {"choice": 1})  # SYMPTOM

    # now go back
    res = send_and_receive(sock, {"action": "BACK"})

    # should return to START
    assert res["state"] == "START"

    sock.close()

def test_partial_flow():
    # this test goes through part of the booking flow
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.recv(4096)  # START

    send_and_receive(sock, {"choice": 1})  # go to SYMPTOM
    send_and_receive(sock, {"choice": 1})  # pick a symptom

    # pick a doctor
    res = send_and_receive(sock, {"choice": 1})

    # depending on priority, it might go to MONTH or TIME
    assert res["state"] in ["MONTH", "TIME"]

    sock.close()

def test_multiple_clients():
    # this test checks if multiple clients can connect at the same time
    clients = []   # storage for all active client sockets

    # create 5 separate client connections to simulate multiple users
    for i in range(5):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        clients.append(sock)

    for sock in clients:
        sock.recv(4096) # receive initial START menu for each client


    # all clients choose book appointment
    for sock in clients:
        sock.sendall((json.dumps({"choice": 1}) + "\n").encode())

    # all clients should move to SYMPTOM
    for sock in clients:
        data = sock.recv(4096).decode().strip()
        response = json.loads(data)

        assert response["state"] == "SYMPTOM"
        # verify all clients transition correctly to SYMPTOM state

    #close all clients
    for sock in clients:
        sock.close()