import socket
import threading
import os
import time
from cryptography.fernet import Fernet
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Claves de encriptación (deben ser iguales en ambos dispositivos)
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# Configuración Bluetooth
LOCAL_MAC = " "
PEER_MAC = " "
PORT = 30

# Carpeta de sincronización
SYNC_FOLDER = "sync_folder"

# Archivo de registro de sincronización
SYNC_LOG = "sync_log.txt"

# Creación de carpeta de sincronización si no existe
if not os.path.exists(SYNC_FOLDER):
    os.makedirs(SYNC_FOLDER)


def encrypt_data(data):
    """Encripta los datos usando la clave definida."""
    return cipher.encrypt(data)


def decrypt_data(data):
    """Desencripta los datos usando la clave definida."""
    return cipher.decrypt(data)


def start_server(local_mac, port):
    """Servidor que escucha y recibe archivos."""
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.bind((local_mac, port))
    sock.listen(1)

    print("Servidor Bluetooth en espera de conexiones...")

    while True:
        client_sock, address = sock.accept()
        print(f"Conexión aceptada de {address[0]}")

        # Recibir encabezado (nombre, tamaño, tipo)
        metadata = decrypt_data(client_sock.recv(1024)).decode()
        operation, filename, filesize = metadata.split("::")
        filesize = int(filesize)

        if operation == "DELETE":
            # Operación de eliminación
            filepath = os.path.join(SYNC_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Archivo eliminado: {filename}")
        else:
            # Operación de recepción de archivo
            print(f"Recibiendo archivo: {filename} ({filesize} bytes)")
            with open(os.path.join(SYNC_FOLDER, filename), "wb") as f:
                received = 0
                while received < filesize:
                    data = decrypt_data(client_sock.recv(1024))
                    f.write(data)
                    received += len(data)

            print(f"Archivo recibido correctamente: {filename}")

        client_sock.close()


def send_file(filepath, peer_mac, port):
    """Cliente que envía un archivo."""
    if not os.path.exists(filepath):
        print("El archivo especificado no existe.")
        return

    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    metadata = f"CREATE::{filename}::{filesize}"

    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
        sock.connect((peer_mac, port))
        sock.send(encrypt_data(metadata.encode()))

        with open(filepath, "rb") as f:
            while chunk := f.read(1024):
                sock.send(encrypt_data(chunk))

    print(f"Archivo enviado correctamente: {filename}")


def send_delete_notification(filename, peer_mac, port):
    """Notifica la eliminación de un archivo."""
    metadata = f"DELETE::{filename}::0"

    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
        sock.connect((peer_mac, port))
        sock.send(encrypt_data(metadata.encode()))

    print(f"Notificación de eliminación enviada: {filename}")


class SyncHandler(FileSystemEventHandler):
    """Manejador de eventos para sincronización."""

    def on_created(self, event):
        if not event.is_directory:
            send_file(event.src_path, PEER_MAC, PORT)

    def on_deleted(self, event):
        if not event.is_directory:
            send_delete_notification(os.path.basename(event.src_path), PEER_MAC, PORT)

    def on_modified(self, event):
        if not event.is_directory:
            send_file(event.src_path, PEER_MAC, PORT)


def start_sync_monitor():
    """Inicia el monitoreo de la carpeta de sincronización."""
    event_handler = SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, SYNC_FOLDER, recursive=True)
    observer.start()
    print(f"Monitoreando cambios en la carpeta: {SYNC_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Iniciar servidor y monitor simultáneamente
server_thread = threading.Thread(target=start_server, args=(LOCAL_MAC, PORT))
server_thread.daemon = True
server_thread.start()

start_sync_monitor()
