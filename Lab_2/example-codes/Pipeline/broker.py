import zmq
import pickle


context = zmq.Context() #aqui creamos un contexto para poder crear sockets y demás cosas de zmq, es como un contenedor de sockets


input_socket = context.socket(   #aqui creamos un socket PULL que nos permite recibir mensajes
    zmq.PULL
)

output_socket = context.socket(  #aqui creamos un socket PUSH que nos permite enviar mensajes
    zmq.PUSH
)


input_socket.bind(               #aqui le conectamos al socket PULL y le asignamos la dirección de conexión
    "tcp://*:13000"
)

output_socket.bind(          #aqui le conectamos al socket PUSH y le asignamos la dirección de conexión
    "tcp://*:13001"
)


print(
    "Broker ready: "
    "input 13000 -> output 13001"
)


while True:

    message = input_socket.recv()   #aqui leemos el mensaje que se envió al socket PULL

    work = pickle.loads(message)    #aqui leemos el mensaje que se envió al socket PULL y lo decodificamos

    print(
        "Broker received:",
        work                        #aqui imprimimos el mensaje que se envió al socket PULL
    )

    output_socket.send(message)     #aqui enviamos el mensaje al socket PUSH

    print(
        "Broker forwarded:",
        work                         #aqui imprimimos el mensaje que se envió al socket PUSH
    )