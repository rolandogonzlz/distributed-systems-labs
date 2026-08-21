from socket import *
import threading

serverName = input("Server IP: ")

if not serverName:
    serverName = "localhost"

serverPort = 22000


def client_task(number):

    clientSocket = socket(AF_INET, SOCK_STREAM)

    try:

        clientSocket.connect((serverName, serverPort))

        message = f"message from client {number}"

        print(f"Client {number} sending: {message}")

        clientSocket.send(message.encode())

        response = clientSocket.recv(1024).decode()

        print(f"Client {number} received: {response}")

    except Exception as e:

        print(f"Client {number} error:", e)

    finally:

        clientSocket.close()


threads = []

for i in range(1, 6):

    thread = threading.Thread(
        target=client_task,
        args=(i,)
    )

    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()

print("All clients finished.")