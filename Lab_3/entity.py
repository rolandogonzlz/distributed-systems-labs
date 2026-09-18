import socket

ENTITY_ID = "studentA-Rolando"
PORT = 50000

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

sock.bind(("", PORT))

print("Entity waiting for location requests...")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()

    if message == ENTITY_ID:
        response = f"{ENTITY_ID}:{socket.gethostbyname(socket.gethostname())}" #esto hace que el mensaje de respuesta sea el id de la entidad y la direccion ip del host donde se encuentra la entidad
        sock.sendto(response.encode(), addr)