from socket import *
import random
import string
import time

serverName = input("Server IP: ")

if not serverName:
    serverName = "localhost"

serverPort = 12000

number_messages = random.randint(3, 7)

print("Number of messages:", number_messages)


for i in range(number_messages):

    clientSocket = socket(AF_INET, SOCK_STREAM)

    try:

        clientSocket.connect((serverName, serverPort))

        message_length = random.randint(5, 15)

        message = ''.join(
            random.choices(
                string.ascii_lowercase,
                k=message_length
            )
        )

        print(f"\nMessage {i + 1}/{number_messages}")
        print("Sending:", message)

        clientSocket.send(message.encode())

        response = clientSocket.recv(1024).decode()

        print("Received:", response)

    except Exception as e:

        print("Error:", e)

    finally:

        clientSocket.close()

    time.sleep(0.5)


print("\nCommunication finished.")
