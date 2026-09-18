import zmq
import threading
import time
import random
import sys
import math

# Configuración de red para K nodos
BASE_PORT = 5550
TOTAL_NODES = 10  # Cambia K al número deseado de nodos (ej. 10, 50, 200)
PORTS = [BASE_PORT + i for i in range(TOTAL_NODES)]

DRIFT_INTERVAL = 3       # Ciclos entre inyecciones de drift
MAX_POLL_TIMEOUT_MS = 800  # Tiempo límite en caso de que no se alcance el quórum

context = zmq.Context.instance()
clock_lock = threading.Lock()
clock_offset = 0.0


def logical_time():
    with clock_lock:
        return time.time() + clock_offset


def time_server(node_id):
    """
    Servidor con socket ROUTER para atender múltiples consultas DEALER de forma asíncrona.
    """
    socket = context.socket(zmq.ROUTER)
    socket.bind(f"tcp://*:{PORTS[node_id]}")
    print(f"Node {node_id} server active on port {PORTS[node_id]}")

    while True:
        try:
            # ROUTER recibe: [identidad_cliente, delimitador_vacio, contenido]
            identity, empty, raw_msg = socket.recv_multipart()
            msg = zmq.utils.jsonapi.loads(raw_msg)

            if msg.get("type") == "TIME":
                reply = {
                    "node": node_id,
                    "time": logical_time()
                }
                socket.send_multipart([
                    identity,
                    b"",
                    zmq.utils.jsonapi.dumps(reply)
                ])
        except Exception as e:
            print(f"Node {node_id} server error: {e}")


def collect_quorum_times(node_id, client_dealer, required_responses):
    """
    Envía peticiones a todos los pares y retorna tan pronto
    como recibe 'required_responses' (K / 2) respuestas.
    """
    times = [logical_time()]
    t_send = logical_time()

    # 1. Disparar solicitud en paralelo a todos los nodos
    for peer_id in range(TOTAL_NODES):
        if peer_id == node_id:
            continue
        try:
            client_dealer.send_multipart(
                [b"", zmq.utils.jsonapi.dumps({"type": "TIME"})],
                flags=zmq.NOBLOCK
            )
        except zmq.ZMQError:
            continue

    # 2. Poller para recolectar respuestas de forma no bloqueante
    poller = zmq.Poller()
    poller.register(client_dealer, zmq.POLLIN)

    start_wait = time.time()
    collected = 0

    while collected < required_responses:
        elapsed_ms = (time.time() - start_wait) * 1000
        remaining_timeout = max(0, int(MAX_POLL_TIMEOUT_MS - elapsed_ms))
        if remaining_timeout == 0:
            break  # Vence el tiempo de espera si faltan respuestas

        events = dict(poller.poll(remaining_timeout))
        if client_dealer in events:
            try:
                empty, raw_resp = client_dealer.recv_multipart(flags=zmq.NOBLOCK)
                response = zmq.utils.jsonapi.loads(raw_resp)
                t_recv = logical_time()

                rtt = t_recv - t_send
                estimated_peer_time = response["time"] + (rtt / 2.0)
                times.append(estimated_peer_time)
                collected += 1
            except (zmq.ZMQError, KeyError):
                break

    return times, collected


def synchronize(node_id):
    global clock_offset
    cycle = 0

    # Quórum objetivo: K // 2 nodos remotos
    required_peers = max(1, TOTAL_NODES // 2)

    # Inicializar socket DEALER conectado a toda la malla
    client_dealer = context.socket(zmq.DEALER)
    client_dealer.setsockopt(zmq.LINGER, 0)
    for peer_id in range(TOTAL_NODES):
        if peer_id != node_id:
            client_dealer.connect(f"tcp://localhost:{PORTS[peer_id]}")

    print(f"Node {node_id} running for K={TOTAL_NODES} nodes. Target Quorum (K/2): {required_peers} responses.")

    while True:
        cycle += 1
        print(f"\n--- Node {node_id} Cycle {cycle} ---")

        # Inyectar drift cada DRIFT_INTERVAL ciclos
        if cycle % DRIFT_INTERVAL == 0:
            drift = random.uniform(-2, 2)
            with clock_lock:
                clock_offset += drift
            print(f"Random drift injected: {drift:+.3f} s")

        own_time = logical_time()
        print(f"My initial time: {own_time:.4f}")

        # Recolectar solo hasta alcanzar el quórum de K / 2
        times, received_count = collect_quorum_times(node_id, client_dealer, required_peers)
        print(f"Quorum status: {received_count}/{required_peers} required responses collected.")

        # Cálculo numéricamente estable de métricas
        t_base = times[0]
        norm_times = [t - t_base for t in times]

        average_norm = sum(norm_times) / len(norm_times)
        average = t_base + average_norm

        current = logical_time()
        clock_skew = average - current

        if len(norm_times) > 1:
            variance = sum((nt - average_norm) ** 2 for nt in norm_times) / (len(norm_times) - 1)
            std_dev = math.sqrt(max(0.0, variance))
        else:
            std_dev = 0.0

        # Ajuste de reloj
        with clock_lock:
            clock_offset += clock_skew

        print(f"Cluster Quorum Average: {average:.4f}")
        print(f"Clock Skew / Correction: {clock_skew:+.4f} s")
        print(f"Cluster Std Dev: {std_dev:.4f} s")
        print(f"Adjusted time: {logical_time():.4f}")

        time.sleep(3)


if __name__ == "__main__":
    try:
        node_id = int(sys.argv[1])
        if node_id not in range(TOTAL_NODES):
            raise ValueError
    except (IndexError, ValueError):
        print(f"Usage: python peer_time.py <node_id> (0 to {TOTAL_NODES - 1})")
        sys.exit(1)

    server_thread = threading.Thread(
        target=time_server,
        args=(node_id,),
        daemon=True
    )
    server_thread.start()

    time.sleep(0.5)

    try:
        synchronize(node_id)
    finally:
        context.term()