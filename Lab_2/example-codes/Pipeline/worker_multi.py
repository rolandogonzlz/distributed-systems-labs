import zmq
import time
import pickle
import sys


if len(sys.argv) > 1:         #aqui verificamos si el usuario ha pasado los argumentos correctamente
    worker_id = sys.argv[1]   #aqui se asigna el id del worker
else:   
    worker_id = "W1"          #aqui se asigna el id del worker


if len(sys.argv) > 2:         #aqui verificamos si el usuario ha pasado los argumentos correctamente
    broker_ip = sys.argv[2]
else:
    broker_ip = "localhost"


context = zmq.Context()       #aqui creamos un contexto para poder crear sockets y demás cosas de zmq, es como un contenedor de sockets

receiver = context.socket(
    zmq.PULL
)


receiver.connect(
    f"tcp://{broker_ip}:13001"
)


print(
    f"Worker {worker_id} "
    f"connected to broker "
    f"{broker_ip}:13001"
)


while True:                   #aqui se ejecuta el ciclo infinito para recibir los mensajes del broker

    work = pickle.loads(        #aqui leemos el mensaje que se envió al socket PULL
        receiver.recv()     
    )

    print(                      #aqui imprimimos el mensaje que se envió al socket PULL
        f"Worker {worker_id} received:",
        work
    )

    time.sleep(
        work["workload"] * 0.1      #aqui se pausa el programa para completar la tarea
    )

    print(
        f"Worker {worker_id} "
        f"completed task "
        f"{work['task']} "
        f"from {work['source']}"
    )