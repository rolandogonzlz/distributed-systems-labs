import xmlrpc.client
import numpy as np


serverName = input(     # Get server name
    "Enter server IP [localhost]: "
).strip()

if not serverName:
    serverName = "localhost"


try:
    serverPort = int(
        input("Enter server port [12000]: ").strip()
        or "12000"
    )
except ValueError:
    serverPort = 12000


proxy = xmlrpc.client.ServerProxy(      # Creamos el que llama al servidor proxy este es el que nos va a devolver los resultados de servidor
    f"http://{serverName}:{serverPort}/RPC2", # URL del servidor
    allow_none=True                     # Permite que los valores nulos sean devueltos por el servidor
)

# Get matrix size   
try:                                   
    n = int(                                                #n es el tamaño de la matriz
        input("Square matrix size n [2]: ").strip()          # Tamaño de la matriz
        or "2"                                              # Tamaño de la matriz
    )
except ValueError:                               # Si el tamaño de la matriz no es un entero        
    n = 2   


operation = input(                            # Operación a realizar
    "Operation (add/sub/prod) [add]: "
).strip().lower()

if not operation:                            # Si no se ingresó una operación
    operation = "add"                         # Se usará la suma


A = np.random.randint(                       # Matriz A aleatoria   
    1,                                       # Rango de los valores
    10,                                       # Tamaño de la matriz
    size=(n, n)                               
)

B = np.random.randint(                       # Matriz B aleatoria
    1,
    10,
    size=(n, n)
)


print("\nMatrix A:")                       # Imprimimos las matrices
print(A)

print("\nMatrix B:")
print(B)

print("\nOperation:")
print(operation)


result = proxy.matrix_operation(             # Llamamos al método matrix_operation del servidor
    A.tolist(),                               # Convertimos las matrices a listas
    B.tolist(),                               
    operation
)


print("\nResult returned by server:")
print(np.array(result))                      # Imprimimos el resultado devuelto por el servidor