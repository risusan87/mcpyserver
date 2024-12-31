
import socket
import threading
from datetime import datetime
from typing import List

from core.logger import logger
import networking.packet as packet
from networking.socket_io import MCPacketInputStream, MCPacketOutputStream
from networking.protocol import ConnectionState
from networking.packet.packet_connection import PacketConnectionState

class ConnectionListener:
    
    def __init__(self):
        self.connections: List[Connection] = []
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
            connection: Connection = connection
            connection.interrupt()
        for connection in self.connections:
            connection.join()
            with self.connection_list_lock:
                self.connections.remove(connection)
        
        self.server.close()
        logger.info('Terminating listener')

    def start_server(self, address='0.0.0.0', port=25565, max_players=20):
        logger.info('Starting server...')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    ###
    # Client connection representation
    # Lifecycle:
    # Call start() to start the connection
    # When the connection is no longer needed, call interrupt() to stop the connection
    # Call join() to wait for the connection to gracefully terminate
    ###

    def __init__(self, client: socket.socket, address, listener: ConnectionListener):
        self.client = client
        self.listener_thread = None
        self.connection_stop_event = threading.Event()
        self.connections_list = listener.connections
        self.lock = listener.connection_list_lock

        # Packet configuration
        self.packet_state = PacketConnectionState()
        self.packet_state.client_ip = address[0]

    def start(self):
        if self.listener_thread:
            logger.warning('Listener already set')
        self.listener_thread = threading.Thread(target=self._handle_connection, name=f'ConnectionListener-{len(self.connections_list)}')
        self.listener_thread.start()        

    def _handle_connection(self):
        input_stream = MCPacketInputStream(self.client, self.packet_state)
        output_stream = MCPacketOutputStream(self.client, self.packet_state)
        while not self.connection_stop_event.is_set():
            if self.packet_state.state == ConnectionState.CLOSE:
                self.interrupt()
                continue
            if input_stream.available() == 0:
                continue
            logger.debug(f'Current connection state is: {self.packet_state.state.name}')
            incoming_packet = input_stream.read_packet(self.packet_state)
            logger.debug(f'Packet received: {incoming_packet.__class__.__name__}')
            if not incoming_packet:
                continue
            response_packet = incoming_packet.handle(self.packet_state)
            if not response_packet:
                continue
            output_stream.write_packet(response_packet)
            output_stream.flush()
            logger.debug(f'Packet sent: {response_packet.__class__.__name__}')

        logger.debug('Connection is shutting down...')
        input_stream.close()
        self.close()

    def interrupt(self):
        self.connection_stop_event.set()

    def join(self):
        self.listener_thread.join()

    def close(self):
        with self.lock:
            self.connections_list.remove(self)
        self.client.close()

    def send(self, data):
        self.client.send(data)

    def recv(self, size):
        return self.client.recv(size)

    def get_connection(self):
        return self.client
