from socket import *
import threading
import time

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverSocket.bind(("", serverPort))
serverSocket.listen(10)

print("Threaded server ready on port", serverPort)


def handle_client(connectionSocket, addr):

    print(f"[THREAD] Client connected: {addr}")

    try:
        sentence = connectionSocket.recv(1024).decode()

        print(f"[{addr}] Received: {sentence}")

        capitalizedSentence = sentence.upper()

        time.sleep(3)

        connectionSocket.send(capitalizedSentence.encode())

        print(f"[{addr}] Response sent")

    except Exception as e:
        print(f"[{addr}] Error:", e)

    finally:
        connectionSocket.close()
        print(f"[{addr}] Connection closed")


while True:

    try:

        connectionSocket, addr = serverSocket.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(connectionSocket, addr)
        )

        thread.start()

        print("Active threads:", threading.active_count() - 1)

    except KeyboardInterrupt:

        print("\nServer shutting down.")
        serverSocket.close()
        break