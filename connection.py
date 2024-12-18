import socket
import threading
import os
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuración
LOCAL_MAC = "E4:A4:71:D5:88:FF"
PEER_MAC = "3C:F0:11:90:2C:60"  # Reemplazar con la dirección MAC del par
PORT = 30
SYNC_FOLDER = "sync_folder"
SYNC_LOG = "sync_log.txt"

if not os.path.exists(SYNC_FOLDER):
    os.makedirs(SYNC_FOLDER)

def log_sync_event(event):
    """Registra eventos de sincronización en el archivo de log."""
    with open(SYNC_LOG, "a") as log_file:
        log_file.write(f"{time.ctime()}: {event}\n")

def get_file_hash(filepath):
    """Calcula el hash MD5 de un archivo."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

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

def handle_client(client_sock):
    """Maneja una conexión cliente individual."""
    try:
        # Recibir encabezado (operación, nombre, tamaño, hash)
        metadata = client_sock.recv(1024).decode()
        operation, filename, filesize, file_hash = metadata.split("::")
        filesize = int(filesize)

        if operation == "DELETE":
            # Operación de eliminación
            filepath = os.path.join(SYNC_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Archivo eliminado: {filename}")
                log_sync_event(f"Archivo eliminado: {filename}")
        elif operation == "CREATE" or operation == "MODIFY":
            # Operación de recepción de archivo
            filepath = os.path.join(SYNC_FOLDER, filename)
            
            # Verificar si el archivo ya existe y tiene el mismo hash
            if os.path.exists(filepath) and get_file_hash(filepath) == file_hash:
                print(f"Archivo {filename} ya está actualizado")
                return

            print(f"Recibiendo archivo: {filename} ({filesize} bytes)")
            log_sync_event(f"Recibiendo archivo: {filename} ({filesize} bytes)")
            
            with open(filepath, "wb") as f:
                received = 0
                while received < filesize:
                    data = client_sock.recv(1024)
                    f.write(data)
                    received += len(data)

            if get_file_hash(filepath) == file_hash:
                print(f"Archivo recibido y verificado correctamente: {filename}")
                log_sync_event(f"Archivo recibido y verificado correctamente: {filename}")
            else:
                print(f"Error: El hash del archivo recibido no coincide: {filename}")
                log_sync_event(f"Error: El hash del archivo recibido no coincide: {filename}")

    except Exception as e:
        print(f"Error al procesar la conexión: {e}")
        log_sync_event(f"Error al procesar la conexión: {e}")
    finally:
        client_sock.close()

def send_file(filepath, peer_mac, port):
    """Cliente que envía un archivo."""
    if not os.path.exists(filepath):
        print(f"El archivo especificado no existe: {filepath}")
        log_sync_event(f"Intento de envío de archivo inexistente: {filepath}")
        return

    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    file_hash = get_file_hash(filepath)
    metadata = f"CREATE::{filename}::{filesize}::{file_hash}"

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
                sock.connect((peer_mac, port))
                sock.send(metadata.encode())

                with open(filepath, "rb") as f:
                    while chunk := f.read(1024):
                        sock.send(chunk)

            print(f"Archivo enviado correctamente: {filename}")
            log_sync_event(f"Archivo enviado correctamente: {filename}")
            return
        except Exception as e:
            print(f"Error al enviar archivo (intento {attempt + 1}): {e}")
            log_sync_event(f"Error al enviar archivo {filename} (intento {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    print(f"No se pudo enviar el archivo {filename} después de {max_retries} intentos.")
    log_sync_event(f"Fallo en el envío del archivo {filename} después de {max_retries} intentos.")

def send_delete_notification(filename, peer_mac, port):
    """Notifica la eliminación de un archivo."""
    metadata = f"DELETE::{filename}::0::0"

    try:
        with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
            sock.connect((peer_mac, port))
            sock.send(metadata.encode())

        print(f"Notificación de eliminación enviada: {filename}")
        log_sync_event(f"Notificación de eliminación enviada: {filename}")
    except Exception as e:
        print(f"Error al enviar notificación de eliminación: {e}")
        log_sync_event(f"Error al enviar notificación de eliminación para {filename}: {e}")

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
    log_sync_event(f"Iniciado monitoreo de la carpeta: {SYNC_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def initial_sync():
    """Realiza una sincronización inicial de todos los archivos en la carpeta."""
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            filepath = os.path.join(root, file)
            send_file(filepath, PEER_MAC, PORT)

if __name__ == "__main__":
    # Iniciar servidor y monitor simultáneamente
    server_thread = threading.Thread(target=start_server, args=(LOCAL_MAC, PORT))
    server_thread.daemon = True
    server_thread.start()

    # Realizar sincronización inicial
    initial_sync()

    # Iniciar monitoreo de cambios
    start_sync_monitor()