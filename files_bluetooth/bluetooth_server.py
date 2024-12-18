

import socket
import time
import threading
from utils import log_sync_event
from file_handler import handle_client

"""
Se configura un servidor Bluetooth que escucha las conexiones entrantes

1. Se crea un socket de Bluetooth
2. Lo enlaza a la direccion MAC local y al puerto
3. Escucha las conexiones entrantes
4. Genera un nuevo subproceos para controlar cada conexion de cliente
"""
def start_server(local_mac, port):
    """Servidor que escucha y recibe archivos."""
    while True:
        try:
            with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
                sock.bind((local_mac, port))
                sock.listen(1)
                print("Servidor Bluetooth en espera de conexiones...")
                log_sync_event("Servidor Bluetooth iniciado")

                while True:
                    client_sock, address = sock.accept()
                    print(f"Conexión aceptada de {address[0]}")
                    log_sync_event(f"Conexión aceptada de {address[0]}")

                    # Iniciar un nuevo hilo para manejar la conexión
                    threading.Thread(target=handle_client, args=(client_sock,)).start()

        except Exception as e:
            print(f"Error en el servidor Bluetooth: {e}. Reiniciando el servidor...")
            log_sync_event(f"Error en el servidor Bluetooth: {e}. Reiniciando el servidor...")
            time.sleep(5)
