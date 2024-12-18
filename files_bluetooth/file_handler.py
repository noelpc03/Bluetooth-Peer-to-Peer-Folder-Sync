
import os
import socket
import time
from config import SYNC_FOLDER
from utils import log_sync_event, get_file_hash



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

