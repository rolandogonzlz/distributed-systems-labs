import zmq


context = zmq.Context()         # Creamos un contexto de zmq y lo asignamos a context

subscriber = context.socket(zmq.SUB)        # Creamos un socket SUB y lo asignamos a s


publisher_count = int(          # publisher_count es el número de publishers que se va a conectar
    input(
        "How many publishers "
        "do you want to connect to? "
    )
)


for i in range(publisher_count):        # Este ciclo se ejecuta para cada publisher que se va a conectar

    host = input(                   # host es la IP del publisher que se va a conectar
        f"Publisher {i + 1} IP [localhost]: "           # Aquí se muestra el mensaje de que se va a pedir la IP del publisher
    ).strip()

    if not host:
        host = "localhost"

    port = int(
        input(
            f"Publisher {i + 1} port: " #aqui se muestra el mensaje de que se va a pedir el puerto del publisher
        )
    )

    endpoint = (
        f"tcp://{host}:{port}" #aqui se muestra el mensaje de que se va a conectar al publisher
    )

    subscriber.connect(endpoint) # se conecta al publisher y se asigna a s endpoint se usa para mostrar el mensaje de que se ha conectado al publisher

    print(
        "Connected to",
        endpoint
    )


topics = input(         #aqui se muestra el mensaje de que se va a pedir los topics que se van a suscribir
    "Topics separated by spaces "
    "(example: TIME RANDOM): "
).upper().split()


for topic in topics:        # Este ciclo se ejecuta para cada topic que se va a suscribir

    subscriber.setsockopt_string( # aqui se muestra el mensaje de que se va a suscribir al topic
        zmq.SUBSCRIBE,
        topic
    )


print(
    "Waiting for messages. "
    "Ctrl+C to stop."
)


while True:         # Este ciclo se ejecuta para recibir los mensajes de los publishers

    message = subscriber.recv_string() # aqui se muestra el mensaje de que se ha recibido un mensaje del publisher

    print(
        "Received:",
        message
    )