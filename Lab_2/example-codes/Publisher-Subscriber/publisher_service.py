import zmq
import time
import random
import sys


if len(sys.argv) < 3:           # esta linea verifica si el usuario ha pasado los argumentos correctamente
    print(
        "Usage: python3 publisher_service.py " # aqui se muestra el uso del programa
        "SERVICE PORT"                        # aqui se muestra el nombre del servicio y el puerto
    )

    print(
        "Example: "
        "python3 publisher_service.py TIME 15001" # aqui se muestra un ejemplo de uso del programa
    )

    sys.exit(1)


service = sys.argv[1].upper() # service es el servicio que se va a publicar
port = int(sys.argv[2])       # port es el puerto que se va a publicar


context = zmq.Context()       # Creamos un contexto de zmq y lo asignamos a context

publisher = context.socket(zmq.PUB)  # Creamos un socket PUB y lo asignamos a s

publisher.bind(                 # Lo conectamos al socket PUB y lo asignamos a s
    f"tcp://*:{port}"           # Creamos una cadena de conexión para el socket PUB
)


print(
    f"Publisher {service} "    # Mensaje de que el servidor está listo 
    f"listening on port {port}..."  # Puerto y nombre del servidor
)


time.sleep(1)                  # Pausamos el programa por 1 segundo

count = 0                      # count es el contador de mensajes


while True:

    count += 1

    if service == "TIME":       # Si el servicio es TIME

        data = time.asctime()       # data es el mensaje que se va a publicar

    elif service == "RANDOM":

        data = str(                # data es el mensaje que se va a publicar y se genera aleatoriamente
            random.randint(1, 100)  # genera un número aleatorio entre 1 y 100
        )

    else:

        data = f"Message #{count}"  #esta linea genera un mensaje con el número de mensaje que se va a publicar


    message = f"{service} {data}"   # message es el mensaje que se va a publicar y se genera con el servicio y el mensaje

    publisher.send_string(message)  # Lo enviamos al socket PUB y se asigna a s

    print("Sent:", message)         # Imprimimos que se ha enviado el mensaje

    time.sleep(2)                   # Pausamos el programa por 2 segundos