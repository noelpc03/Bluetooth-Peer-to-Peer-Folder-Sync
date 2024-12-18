# Bluetooth Peer-to-Peer Folder Sync

Este proyecto implementa un servicio para la sincronización bidireccional de carpetas entre dos ordenadores utilizando Bluetooth. Está diseñado para asegurar que los cambios en cualquiera de las carpetas sincronizadas se reflejen automáticamente en el otro dispositivo, incluso en situaciones de desconexión temporal.

## 🚀 Características

- **Sincronización en tiempo real:** Los cambios en una carpeta (creación, modificación, eliminación) se propagan automáticamente al otro ordenador.
- **Resiliencia:** El programa maneja errores y garantiza su funcionamiento continuo incluso si un dispositivo se desconecta.

- **Interfaz sencilla:** Ejecutable desde la línea de comandos con mensajes claros y estados de operación.

## 📁 Estructura del Proyecto

```
bluetooth_folder_sync/
├── connection.py  # Código principal del proyecto
├── sync_folder/              # Carpeta sincronizada (se crea automáticamente)
├── sync_log.txt              # Registro de sincronización
```

## 🛠️ Requisitos

1. **Python 3.9 o superior**
2. **Libraries Used:**

   - `socket`:: For Bluetooth communication
   - `threading`: For running server and file monitoring concurrently
   - `os`: For file and directory operations
   - `time`: For timestamps and delays
   - `hashlib`: For calculating file hashes
   - `watchdog`: For monitoring file system events

3. **Bluetooth habilitado:** Tanto hardware como software deben ser compatibles con Bluetooth.

## 🔧 Configuración

1. Configura las direcciones MAC de los dispositivos en `bluetooth_folder_sync.py`:

   ```python
   LOCAL_MAC = "XX:XX:XX:XX:XX:XX"  # Dirección MAC del dispositivo local
   PEER_MAC = "YY:YY:YY:YY:YY:YY"   # Dirección MAC del dispositivo remoto
   ```
2. Personaliza la carpeta de sincronización, si es necesario:

   ```python
   SYNC_FOLDER = "sync_folder"
   ```
3. Asegúrate de que ambos dispositivos tienen la misma clave de cifrado en la variable `ENCRYPTION_KEY`.

4.  Instalar las importanciones necesarias para ejecutar el script

```python
   python -m pip install -r requirements.txt
   ``` 

## 📖 Uso

### 1. Configurar el entorno

- En ambos dispositivos, clona el repositorio y edita las configuraciones necesarias.

### 2. Ejecutar el programa

Inicia el script en ambos dispositivos:

```bash
python connection.py
```

El programa comenzará a monitorear cambios en la carpeta definida y sincronizará los archivos automáticamente.


### 3.Terminos importantes

- `socket`: es una API que permite la  comunicación entre dos procesos (programas) a través de una red. Esencialmente, un socket actúa como un punto final para enviar y recibir datos entre dispositivos, ya sea en una red local o a través de Internet.
