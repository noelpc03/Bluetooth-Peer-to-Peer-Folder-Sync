

import threading
from bluetooth_server import start_server
from sync_monitor import start_sync_monitor, initial_sync

if __name__ == "__main__":
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    
    initial_sync()

    
    start_sync_monitor()