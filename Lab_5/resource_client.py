import zmq
import sys
import time
import random

SERVER = "tcp://localhost:6500"

if len(sys.argv) != 2:
    print("Usage: python resource_client.py <client_name>")
    sys.exit(1)

client = sys.argv[1]

context = zmq.Context.instance()


def create_req_socket():
    """Crea y configura el socket REQ con timeouts definidos."""
    s = context.socket(zmq.REQ)
    s.setsockopt(zmq.RCVTIMEO, 3000)
    s.setsockopt(zmq.SNDTIMEO, 3000)
    s.setsockopt(zmq.LINGER, 0)
    s.connect(SERVER)
    return s


# Socket persistente único
socket = create_req_socket()


def send_request(message):
    """Envía peticiones reutilizando el socket y manejando desincronizaciones de ZMQ."""
    global socket
    try:
        socket.send_json(message)
        return socket.recv_json()
    except (zmq.error.Again, Exception):
        # La máquina de estados de un socket REQ se rompe tras un timeout.
        # Se recicla el socket únicamente cuando ocurre un fallo real.
        socket.close(linger=0)
        socket = create_req_socket()
        return {"status": "TIMEOUT", "message": "Server unreachable"}


try:
    for cycle in range(3):
        print(f"\n[{client}] --- Cycle {cycle + 1}/3: Requesting resource ---")

        # Bucle de espera pasiva/reintento
        while True:
            response = send_request({
                "action": "ACQUIRE",
                "client": client
            })

            status = response.get("status")

            if status == "GRANTED":
                break
            elif status == "BUSY":
                print(f"[{client}] Resource busy (Owner: {response.get('owner')}), waiting...")
            elif status == "TIMEOUT":
                print(f"[{client}] Warning: Server timeout. Retrying...")
            else:
                print(f"[{client}] Unexpected error: {response.get('message')}")

            time.sleep(1)

        print(f"[{client}] >>> ENTERS critical section <<<")
        work_time = random.uniform(2, 5)
        time.sleep(work_time)
        print(f"[{client}] <<< LEAVES critical section >>>")

        # Liberación con confirmación
        rel_resp = send_request({
            "action": "RELEASE",
            "client": client
        })
        if rel_resp.get("status") != "RELEASED":
            print(f"[{client}] Error releasing resource: {rel_resp.get('message')}")

        time.sleep(random.uniform(1, 3))

finally:
    socket.close(linger=0)
    context.term()