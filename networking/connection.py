
import socket
import threading
from datetime import datetime
from typing import List

from core.logger import logger
import networking.packet as packet
from networking.packet.client_bound import configuration as c_config
from networking.packet.server_bound import configuration as s_config
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

        # For server initiated connections
        self.bundle_lock = threading.Lock()
        self.bundle = []
        self.response_lock = threading.Condition()
        self.response = None

    def start(self):
        if self.listener_thread:
            logger.warning('Listener already set')
        self.packet_state.connection_id = len(self.connections_list)
        self.listener_thread = threading.Thread(target=self._handle_connection, name=f'ConnectionListener-{len(self.connections_list)}')
        self.listener_thread.start()   
    
    def send_packet(self, *clientbound_packets: packet.ClientboundPacket) -> packet.ServerboundPacket:
        '''
        Queue packets to be sent to the client.
        Packets given in this function are guranteed to be sent in the order they are given as soon as next opportunity within network flow is available, and receives a response from the client.

        Packets can be sent as a bundle as long as it won't break the protocol.
        Generally, bundle packets are only acceptable in play state, where packets are surrounded by bundle delimiters (id = 0x00).
        As of 1.20.6, the Notchian server only uses bundle delimiter to ensure Spawn Entity and associated packets used to configure the entity happen on the same tick. 
        Each entity gets a separate bundle. 
        The Notchian client doesn't allow more than 4096 packets in the same bundle.
        '''
        with self.response_lock:
            self.response = None
        with self.bundle_lock:
            self.bundle.extend(clientbound_packets)
        with self.response_lock:
            while not self.response:
                self.response_lock.wait()
        return self.response

    def _per_connection_configuration(self, input_stream, output_stream):
        '''
        Define sequence of packets to be sent to the client to configure the connection.
        Packets here are sent during configuration state, after receiving the client information packet (SConfig/0x00) and before finish configuration (CConfig/0x03).
        '''
        pass     

    def _handle_connection(self):
        # i/o streams
        input_stream = MCPacketInputStream(self.client, self.packet_state)
        output_stream = MCPacketOutputStream(self.client, self.packet_state)

        while not self.connection_stop_event.is_set():
            if self.packet_state.state == ConnectionState.CLOSE:
                self.interrupt()
                continue

            if input_stream.available() == 0:
                ### Server initiated connection ###

                # Per-connection initial configuration
                if self.packet_state.state == ConnectionState.CONFIGURATION:
                    with self.packet_state.client_information_lock:
                        if self.packet_state.client_information_config_ready and not self.packet_state.client_information_initial_config_flag:
                            self._per_connection_configuration(input_stream, output_stream)
                            output_stream.write_packet(c_config.CFinishConfiguration())
                            output_stream.flush()
                            logger.debug(f'Sent Finish Configuration packet')
                            config_acknowledgement = input_stream.read_packet(self.packet_state)
                            if not isinstance(config_acknowledgement, s_config.SFinishConfigurationAcknowledged):
                                logger.error(f'Invalid packet received: {config_acknowledgement.__class__.__name__}')
                                self.interrupt()
                                continue
                            config_acknowledgement.handle(self.packet_state)
                            self.packet_state.client_information_initial_config_flag = True
                            logger.debug('Initial configuration completed')
                            continue

                # Flush packets in queue
                with self.bundle_lock:
                    if self.bundle:
                        for packets in self.bundle:
                            output_stream.write_packet(packets)
                        output_stream.flush()
                        self.bundle = []
                        with self.response_lock:
                            self.response = input_stream.read_packet(self.packet_state)
                            self.response_lock.notify()
                continue

            ### Client initiated connection ###
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

    def get_connection(self):
        return self.client
        
