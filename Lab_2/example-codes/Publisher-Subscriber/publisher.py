import zmq, time            # zmq es el módulo de python que nos permite usar ZeroMQ

context = zmq.Context()     # Creamos un contexto de zmq y lo asignamos a context
s = context.socket(zmq.PUB)  # Creamos un socket PUB y lo asignamos a s

serverName = input("Enter server hostname or IP address: ")
if not serverName:
    serverName = "localhost"
try:
    serverPort = int(input("Enter server port number: "))
except:
    print("Invalid input. Using default port 15000.")
    serverPort = 15000

if serverPort <= 0 or serverPort > 65535:   # Si el puerto no es correcto o no es un número entero, se asigna el puerto 15000
    serverPort = 15000                      # Asignamos el puerto 15000

p = "tcp://" + serverName + ":" + str(serverPort)  # Creamos una cadena de conexión para el socket PUB
s.bind(p)                                       # Lo conectamos al socket PUB y lo asignamos a s

cont = 0
while True:
    time.sleep(5)
    cont += 1
    s.send(("TIME " + time.asctime() + " - Message #" + str(cont)).encode("utf-8"))

