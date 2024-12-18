
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import SYNC_FOLDER,SYNC_LOG,PEER_MAC,PORT
from utils import log_sync_event
from file_handler import send_file, send_delete_notification


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
