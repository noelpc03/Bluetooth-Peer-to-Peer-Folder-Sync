
# Bluetooth Peer-to-Peer Folder Sync

Este proyecto implementa un servicio para la sincronización bidireccional de carpetas entre dos ordenadores utilizando Bluetooth. Está diseñado para asegurar que los cambios en cualquiera de las carpetas sincronizadas se reflejen automáticamente en el otro dispositivo, incluso en situaciones de desconexión temporal.

## 🚀 Características

- **Sincronización en tiempo real:** Los cambios en una carpeta (creación, modificación, eliminación) se propagan automáticamente al otro ordenador.
- **Seguridad:** Los datos se cifran utilizando el módulo `cryptography` para proteger la transferencia.
- **Resiliencia:** El programa maneja errores y garantiza su funcionamiento continuo incluso si un dispositivo se desconecta.
- **Resolución de conflictos:** Identifica y gestiona versiones distintas de un archivo tras una desconexión.
- **Interfaz sencilla:** Ejecutable desde la línea de comandos con mensajes claros y estados de operación.

## 📁 Estructura del Proyecto

```
bluetooth_folder_sync/
├── bluetooth_folder_sync.py  # Código principal del proyecto
├── sync_folder/              # Carpeta sincronizada (se crea automáticamente)
├── sync_log.txt              # Registro de sincronización
```

## 🛠️ Requisitos

1. **Python 3.9 o superior**
2. **Dependencias:** Instalar con `pip install -r requirements.txt`:
   - `cryptography`
   - `watchdog`

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

## 📖 Uso

### 1. Configurar el entorno
- En ambos dispositivos, clona el repositorio y edita las configuraciones necesarias.
- Instala las dependencias con `pip install -r requirements.txt`.

### 2. Ejecutar el programa
Inicia el script en ambos dispositivos:
```bash
python bluetooth_folder_sync.py
```

El programa comenzará a monitorear cambios en la carpeta definida y sincronizará los archivos automáticamente.

### 3. Manejo de conflictos
Si tras una desconexión se detectan dos versiones de un archivo, el programa:
- Creará copias con sufijos de nombre (`_local` y `_remote`) para evitar sobrescrituras.
- Permitirá a los usuarios decidir qué versión conservar.

