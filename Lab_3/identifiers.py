import uuid
import socket

entity_id = uuid.uuid5(uuid.NAMESPACE_DNS, "rol-gonzalez.es")
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print("Entity ID :", entity_id)
print("Hostname :", hostname)
print("Address :", ip)

entity = {
    "id": str(entity_id),
    "address": (ip,5000)
}

print("\nEntity:")
print(entity)

print("\nBefore moving:")
print(entity)

entity["address"] = (ip,6000)
print("\nAfter moving:")
print(entity)