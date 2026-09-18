import zmq
import sys
import time
import random

PORTS = [7001, 7002, 7003]
N = len(PORTS)

try:
    node_id = int(sys.argv[1])
    if node_id not in range(N):
        raise ValueError
except (IndexError, ValueError):
    print("Usage: python token_ring_node.py <0|1|2>")
    sys.exit(1)

next_node = (node_id + 1) % N

context = zmq.Context.instance()

receiver = context.socket(zmq.PULL)
receiver.bind(f"tcp://*:{PORTS[node_id]}")

sender = context.socket(zmq.PUSH)
sender.setsockopt(zmq.LINGER, 0)
sender.connect(f"tcp://localhost:{PORTS[next_node]}")

print(f"P{node_id} ready | Forwarding to -> P{next_node}")

has_token = (node_id == 0)

if has_token:
    print("P0 owns initial TOKEN. Waiting 5s for network convergence...")
    time.sleep(5)

# Carga útil optimizada: bytes planos en lugar de serialización JSON repetitiva
TOKEN_PAYLOAD = b"TOKEN"

try:
    while True:
        if not has_token:
            # Espera bloqueante sin consumo de CPU (impulsado por eventos)
            raw_msg = receiver.recv()
            if raw_msg == TOKEN_PAYLOAD:
                has_token = True
                print(f"\nP{node_id} received TOKEN")

        if has_token:
            wants_resource = (random.random() < 0.7)

            if wants_resource:
                print(f"P{node_id} ENTERS critical section")
                time.sleep(random.uniform(1, 3))
                print(f"P{node_id} LEAVES critical section")
            else:
                print(f"P{node_id} does not need resource")
                # Evita que el token gire descontrolado saturando la red
                time.sleep(0.3)

            print(f"P{node_id} passes TOKEN to P{next_node}")
            sender.send(TOKEN_PAYLOAD)
            has_token = False

except KeyboardInterrupt:
    print(f"\nP{node_id} shutting down cleanly...")
finally:
    receiver.close(linger=0)
    sender.close(linger=0)
    context.term()