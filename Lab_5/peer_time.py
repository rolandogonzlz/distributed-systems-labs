import zmq
import threading
import time
import random
import sys
import math

PORTS = [
    5551,
    5552,
    5553
]

K = 3

context = zmq.Context.instance()
clock_lock = threading.Lock()
clock_offset = 0.0

# Almacenamiento persistente de sockets de clientes (REQ)
peer_sockets = {}


def logical_time():
    with clock_lock:
        return time.time() + clock_offset


def time_server(node_id):
    """Hilo servidor: responde a peticiones de hora de otros nodos."""
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORTS[node_id]}")
    print(f"Node {node_id} listening on port {PORTS[node_id]}")

    while True:
        try:
            message = socket.recv_json()
            if message.get("type") == "TIME":
                socket.send_json({
                    "node": node_id,
                    "time": logical_time()
                })
            else:
                socket.send_json({
                    "error": "Invalid request"
                })
        except Exception as e:
            print(f"Node {node_id} server error: {e}")


def init_peer_sockets(node_id):
    """Crea y configura los sockets hacia los pares una sola vez."""
    global peer_sockets
    for peer_id, port in enumerate(PORTS):
        if peer_id == node_id:
            continue

        s = context.socket(zmq.REQ)
        s.setsockopt(zmq.RCVTIMEO, 1000)
        s.setsockopt(zmq.SNDTIMEO, 1000)
        s.setsockopt(zmq.LINGER, 0)
        s.connect(f"tcp://localhost:{port}")
        peer_sockets[peer_id] = s


def recreate_peer_socket(peer_id):
    """Reinicia un socket específico si queda en estado inconsistente tras un timeout."""
    global peer_sockets
    try:
        peer_sockets[peer_id].close(linger=0)
    except Exception:
        pass

    s = context.socket(zmq.REQ)
    s.setsockopt(zmq.RCVTIMEO, 1000)
    s.setsockopt(zmq.SNDTIMEO, 1000)
    s.setsockopt(zmq.LINGER, 0)
    s.connect(f"tcp://localhost:{PORTS[peer_id]}")
    peer_sockets[peer_id] = s


def request_time(peer_id):
    """
    Reutiliza el socket persistente y compensa la latencia (RTT / 2)
    siguiendo el principio del algoritmo de Cristian / NTP.
    """
    s = peer_sockets[peer_id]
    t_send = logical_time()

    try:
        s.send_json({"type": "TIME"})
        response = s.recv_json()
        t_recv = logical_time()

        rtt = t_recv - t_send
        estimated_time = response["time"] + (rtt / 2.0)
        return estimated_time, rtt

    except (zmq.error.Again, Exception):
        recreate_peer_socket(peer_id)
        return None, None


def synchronize(node_id):
    global clock_offset
    cycle = 0

    init_peer_sockets(node_id)

    while True:
        cycle += 1
        print(f"\n--- Node {node_id} Cycle {cycle} ---")

        # Inyectar drift artificial cada K ciclos
        if cycle % K == 0:
            drift = random.uniform(-2, 2)
            with clock_lock:
                clock_offset += drift
            print(f"Random drift injected: {drift:+.3f} s")

        own_time = logical_time()
        times = [own_time]
        print(f"My initial time: {own_time:.4f}")

        # Consultar a los compañeros
        for peer_id in peer_sockets:
            peer_time, rtt = request_time(peer_id)
            if peer_time is not None:
                times.append(peer_time)
                print(f"Node {peer_id}: {peer_time:.4f} (RTT: {rtt:.4f} s)")

        # -----------------------------------------------------------------
        # CÁLCULO NUMÉRICAMENTE ESTABLE DE MÉTRICAS (SIN NEGATIVOS EN STD)
        # -----------------------------------------------------------------
        # 1. Normalización para prevenir cancelación por punto flotante
        t_base = times[0]
        norm_times = [t - t_base for t in times]

        # 2. Media aritmética
        average_norm = sum(norm_times) / len(norm_times)
        average = t_base + average_norm

        # 3. Clock Skew / Offset (esta resta sí puede ser positiva o negativa)
        current = logical_time()
        clock_skew = average - current

        # 4. Desviación estándar de la muestra (garantizada >= 0.0)
        if len(norm_times) > 1:
            variance = sum((nt - average_norm) ** 2 for nt in norm_times) / (len(norm_times) - 1)
            std_dev = math.sqrt(max(0.0, variance))
        else:
            std_dev = 0.0

        # Aplicar el ajuste al reloj lógico
        with clock_lock:
            clock_offset += clock_skew

        print(f"Cluster Average: {average:.4f}")
        print(f"Clock Skew / Correction: {clock_skew:+.4f} s (Signo: desfase relativo)")
        print(f"Cluster Std Dev: {std_dev:.4f} s (Dispersión: siempre >= 0)")
        print(f"Adjusted time: {logical_time():.4f}")

        time.sleep(3)


if __name__ == "__main__":
    try:
        node_id = int(sys.argv[1])
        if node_id not in range(len(PORTS)):
            raise ValueError
    except (IndexError, ValueError):
        print("Usage: python peer_time.py <node_id>")
        print("Example: python peer_time.py 0")
        sys.exit(1)

    server_thread = threading.Thread(
        target=time_server,
        args=(node_id,),
        daemon=True
    )
    server_thread.start()

    time.sleep(1)

    try:
        synchronize(node_id)
    finally:
        for s in peer_sockets.values():
            s.close(linger=0)
        context.term()