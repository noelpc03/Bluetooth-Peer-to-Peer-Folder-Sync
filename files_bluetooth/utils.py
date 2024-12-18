

import os
import time
import hashlib
from config import SYNC_FOLDER,SYNC_LOG

"""Chequear si el directorio del SYNC_FOLDER existe
    si no , crea el directorio
""" 
if not os.path.exists(SYNC_FOLDER):
    os.makedirs(SYNC_FOLDER)

def log_sync_event(event):
    """Registra eventos de sincronización en el archivo de log."""
    with open(SYNC_LOG, "a") as log_file:
        log_file.write(f"{time.ctime()}: {event}\n")

def get_file_hash(filepath):
    """Calcula el hash MD5 de un archivo."""
    hasher = hashlib.md5() # creacion del hasher usando el algoritmo MD5 del modulo hashlib
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()
