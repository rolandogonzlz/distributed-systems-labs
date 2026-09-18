from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import numpy as np 


class RequestHandler(SimpleXMLRPCRequestHandler):       # Creamos el que llama al servidor proxy este es el que nos va a devolver los resultados de servidor
    rpc_paths = ('/RPC2',)                              # Restringe a una ruta y no a otra


serverName = input("Enter server hostname/IP [0.0.0.0]: ").strip()  # Get server name

if not serverName:
    serverName = "0.0.0.0"


try:
    serverPort = int(
        input("Enter server port [12000]: ").strip() or "12000"
    )
except ValueError:
    serverPort = 12000


if serverPort <= 0 or serverPort > 65535:               # Si el puerto no es correcto o no es un número entero, se asigna el puerto 12000
    serverPort = 12000


def matrix_operation(matrix_a, matrix_b, operation):             # Función que recibe los parámetros de la llamada del método

    A = np.array(matrix_a)                                  # Convertimos los parámetros a matrices
    B = np.array(matrix_b)

    if operation == "add":                                  # Si la operación es la suma
        result = A + B

    elif operation == "sub":
        result = A - B

    elif operation == "prod":                 # Si la operación es la multiplicación
        result = np.matmul(A, B)

    else:
        raise ValueError(
            "Invalid operation. Use add, sub or prod."
        )

    print("\nOperation received:", operation)               # Imprimimos la operación recibida

    print("\nMatrix A:")
    print(A)

    print("\nMatrix B:")
    print(B)

    print("\nResult:")
    print(result)

    return result.tolist()                                  # Devolvemos el resultado como lista


with SimpleXMLRPCServer(                                   # Creamos el servidor y le asignamos el puerto y el nombre del servidor
    (serverName, serverPort),                              # Puerto y nombre del servidor
    requestHandler=RequestHandler,                         # Creamos el que llama al servidor proxy este es el que nos va a devolver los resultados de servidor 
    allow_none=True                                        # Permite que los valores nulos sean devueltos por el servidor   
) as server:                                               # Creamos el servidor y le asignamos el puerto y el nombre del servidor

    server.register_introspection_functions()               # Registramos las funciones de introspección    

    server.register_function(                               # Registramos la función que recibe los parámetros de la llamada del método y devuelve el resultado
        matrix_operation,                                   # Función que recibe los parámetros de la llamada del método    
        "matrix_operation"                                  # Nombre de la función y del método que llama
    )

    print(                                                  # Imprimimos que el servidor está listo
        f"Matrix server listening on "                      # Mensaje de que el servidor está listo
        f"{serverName}:{serverPort}..."                     # Puerto y nombre del servidor
    )

    server.serve_forever()                                  # Ejecutamos el servidor