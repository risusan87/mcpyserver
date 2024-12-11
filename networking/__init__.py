
from networking.connection import ConnectionListener

listener = None

def start_server():
    global listener
    listener = ConnectionListener()
    listener.start_server()

def stop_server():
    global listener
    listener.stop_server()