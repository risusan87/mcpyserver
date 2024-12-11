
import socket
import threading
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection
from logger import logger

class ConnectionListener:
    
    def __init__(self):
        self.connections = []
        self.connection_list_lock = threading.Lock()
        self.server_stop_event = threading.Event()
        self.server_thread = None
        self.server = None


    def listen_connection(self):
        logger.info('Listening for connections...')
        while not self.server_stop_event.is_set():
            try:
                client, addr = self.server.accept()
            except socket.timeout:
                continue
            con = Connection(client, addr, self)
            con.start()
            with self.connection_list_lock:
                self.connections.append(con)
        logger.info('Connection listener is shutting down...')
        for connection in self.connections:
            connection.interrupt()
        for connection in self.connections:
            connection.join()
        self.server.close()
        logger.info('Terminating listener')

    def start_server(self, address='0.0.0.0', port=25565, max_players=20):
        logger.info('Starting server...')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(1)
        self.server.settimeout(1.0)
        self.server_thread = threading.Thread(target=self.listen_connection, name='ConnectionListener')
        self.server_thread.start()
        logger.info('Server started!')
    
    def stop_server(self):
        if not self.server_thread:
            logger.warning(f'Connection listener not started.')
            return
        self.server_stop_event.set()
        self.server_thread.join()

class Connection:
    def __init__(self, client: socket.socket, address, listener: ConnectionListener):
        self.client = client
        self.address = address
        self.listener_thread = None
        self.connection_stop_event = threading.Event()
        self.connections_list = listener.connections
        self.lock = listener.connection_list_lock

    def start(self):
        if self.listener_thread:
            logger.warning('Listener already set')
        self.listener_thread = threading.Thread(target=self.handle_connection, name=f'ConnectionListener-{len(self.connections_list)}')
        self.listener_thread.start()
    
    def handle_connection(self):
        try:
            msg = self.recv(1024)
        except OSError:
            logger.error('Client unexpectedly disconnected. If you weren\'t expecting this error, check Firewall settings.')
            with self.lock:
                self.connections_list.remove(self)
            return
        logger.info(f'{msg}')
        self.send()
        self.client.close()

    def interrupt(self):
        self.connection_stop_event.set()

    def join(self):
        self.listener_thread.join()


    def send(self, data):
        self.client.send(data)

    def recv(self, size):
        return self.client.recv(size)

    def get_connection(self):
        return self.client