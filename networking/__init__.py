
from networking.connection import ConnectionListener

_listener = None

def start_server(port=25565):
    global _listener
    _listener = ConnectionListener()
    _listener.start_server(port=port)

def stop_server():
    global _listener
    _listener.stop_server()
    