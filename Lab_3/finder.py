import socket

ENTITY_ID = "myte"
PORT = 50001

sock = socket.socket( #aqui hacemos un socket UDP para buscar la entidad
    socket.AF_INET,   # luego hacemos un broadcast para buscar la entidad en la red
    socket.SOCK_DGRAM
)

sock.setsockopt(      #de igual manera hacemos un set option para permitir el broadcast
    socket.SOL_SOCKET, #luego hacemos un set timeout para que no se quede esperando indefinidamente
    socket.SO_BROADCAST,
    1
)

sock.settimeout(3)    # sirve para que el socket no se quede esperando indefinidamente, si no encuentra la entidad en 3 segundos, se sale del bucle

sock.sendto(
    ENTITY_ID.encode(),
    ("255.255.255.255", PORT)
)

try:            #hacemos un try para recibir la respuesta de la entidad, si no la encuentra en 3 segundos, se sale del bucle
    data, addr = sock.recvfrom(1024)   #aqui recibimos la respuesta de la entidad, si la encuentra, imprime el mensaje de que la entidad fue encontrada

    print(
        "Entity found:",
        data.decode()
    )

except socket.timeout:      # hacemos un except para manejar el caso en que no se encuentra la entidad, imprime un mensaje de que la entidad no fue encontrada
    print("Entity not found")