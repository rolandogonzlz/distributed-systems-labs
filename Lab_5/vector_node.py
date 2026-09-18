import zmq
import threading
import sys
import time

PORTS = [6001, 6002, 6003]
N = len(PORTS)

context = zmq.Context.instance()
clock_lock = threading.Lock()


def receiver(node_id, vector):
    socket = context.socket(zmq.PULL)
    socket.bind(f"tcp://*:{PORTS[node_id]}")
    print(f"Node {node_id} listening on port {PORTS[node_id]}")

    while True:
        try:
            # Bloqueo eficiente impulsado por eventos (sin despertar cada 500ms)
            message = socket.recv_json()

            # Mensaje especial para terminar limpiamente el hilo
            if message.get("type") == "SHUTDOWN":
                break

            received_vector = message["vector"]
            sender = message["sender"]
            text = message["message"]

            with clock_lock:
                # Regla de actualización de relojes vectoriales
                for i in range(N):
                    vector[i] = max(vector[i], received_vector[i])
                vector[node_id] += 1
                current = vector.copy()

            print(f"\nReceived from P{sender}: {text}")
            print(f"Received vector: {received_vector}")
            print(f"Updated vector:  {current}")
            print("> ", end="", flush=True)

        except zmq.ContextTerminated:
            break
        except Exception as e:
            print(f"\nReceiver error: {e}")
            break

    socket.close(linger=0)


def main(node_id):
    vector = [0] * N
    senders = {}

    # Inicialización única de sockets PUSH persistentes
    for peer_id in range(N):
        if peer_id != node_id:
            sock = context.socket(zmq.PUSH)
            sock.setsockopt(zmq.LINGER, 0)
            sock.connect(f"tcp://localhost:{PORTS[peer_id]}")
            senders[peer_id] = sock

    thread = threading.Thread(
        target=receiver,
        args=(node_id, vector),
        daemon=True
    )
    thread.start()

    time.sleep(0.5)

    print("\nCommands: event | send <node> <message> | show | quit")

    while True:
        try:
            command = input("> ").strip()
            if not command:
                continue

            if command == "event":
                with clock_lock:
                    vector[node_id] += 1
                    current = vector.copy()
                print(f"Internal event -> {current}")

            elif command == "show":
                with clock_lock:
                    current = vector.copy()
                print(f"Vector: {current}")

            elif command.startswith("send "):
                parts = command.split(" ", 2)
                if len(parts) != 3:
                    print("Use: send <node> <message>")
                    continue

                target = int(parts[1])
                text = parts[2]

                if target == node_id or target not in senders:
                    print("Invalid destination")
                    continue

                # Actualización de evento local de envío
                with clock_lock:
                    vector[node_id] += 1
                    message_vector = vector.copy()

                senders[target].send_json({
                    "sender": node_id,
                    "message": text,
                    "vector": message_vector
                })

                print(f"Sent to P{target}")
                print(f"Vector: {message_vector}")

            elif command == "quit":
                break

            else:
                print("Invalid command")

        except ValueError:
            print("Invalid node number")
        except (KeyboardInterrupt, EOFError):
            break

    # Cierre ordenado y liberación de recursos
    # Se envía un mensaje local para desbloquear el socket PULL sin esperar timeouts
    shutdown_sock = context.socket(zmq.PUSH)
    shutdown_sock.connect(f"tcp://localhost:{PORTS[node_id]}")
    shutdown_sock.send_json({"type": "SHUTDOWN"})
    shutdown_sock.close(linger=0)

    thread.join(timeout=1)
    for s in senders.values():
        s.close(linger=0)
    context.term()


if __name__ == "__main__":
    try:
        node_id = int(sys.argv[1])
        if node_id not in range(N):
            raise ValueError
    except (IndexError, ValueError):
        print("Usage: python vector_node.py <0|1|2>")
        sys.exit(1)

    main(node_id)