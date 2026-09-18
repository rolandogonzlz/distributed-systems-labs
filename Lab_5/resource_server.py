import zmq
import time

PORT = 6500

context = zmq.Context.instance()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{PORT}")

owner = None
lease_timeout = 10.0  # Segundos máximos que un cliente puede retener el recurso sin renovar
last_acquired_time = 0.0

print(f"Resource Manager running on port {PORT}")

while True:
    try:
        request = socket.recv_json()
    except Exception as e:
        print(f"Error al recibir: {e}")
        continue

    response = {"status": "ERROR", "message": "Unknown error"}

    try:
        action = request.get("action")
        client = request.get("client")
        current_time = time.time()

        # Comprobar si el dueño actual excedió el lease (evita bloqueos si el cliente muere)
        if owner is not None and (current_time - last_acquired_time > lease_timeout):
            print(f"Lease expirado para {owner}. Recurso liberado automáticamente.")
            owner = None

        if not client:
            response = {"status": "ERROR", "message": "Missing client"}

        elif action == "ACQUIRE":
            if owner is None:
                owner = client
                last_acquired_time = current_time
                print(f"Resource granted to {client}")
                response = {"status": "GRANTED"}
            elif owner == client:
                last_acquired_time = current_time  # Renueva el lease
                response = {"status": "GRANTED"}
            else:
                response = {"status": "BUSY", "owner": owner}

        elif action == "RELEASE":
            if owner == client:
                print(f"Resource released by {client}")
                owner = None
                response = {"status": "RELEASED"}
            else:
                response = {"status": "ERROR", "message": "Client does not own resource"}

        else:
            response = {"status": "ERROR", "message": "Invalid action"}

    except Exception as e:
        print(f"Server error: {e}")
        response = {"status": "ERROR", "message": f"Internal error: {str(e)}"}

    # Garantiza que SIEMPRE se envíe una respuesta, protegiendo la máquina de estados del socket REP
    socket.send_json(response)