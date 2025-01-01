
import socket
import threading
import struct

from cryptography.hazmat.primitives.ciphers import CipherContext

import networking.packet as packet
from networking.packet.server_bound import handshake as s_handshake
from networking.packet.server_bound import status as s_status
from networking.packet.server_bound import login as s_login
from networking.packet.server_bound import configuration as s_config
from networking.packet.packet_connection import PacketConnectionState

from networking.data_type import ByteBuffer, BufferedPacket
from core.logger import logger
from networking.protocol import ConnectionState, ProtocolVersion
from networking.exception import ProtocolError, DataCorruptedError

class ConnectionInputStream:
    def __init__(self, socket: socket.socket, p_state: PacketConnectionState, byte_order='big'):
        self._byte_order = byte_order

        self._buffer = ByteBuffer(byte_order=self._byte_order)
        '''
        Do not touch this
        '''

        self._socket = socket
        self._input_thread_event = threading.Event()
        self._buffer_lock = threading.Lock()
        self._available = 0
        self._p_state = p_state

        # Start read thread
        self._socket.settimeout(0.1)
        self._input_thread = threading.Thread(target=self._read_data, name=f'ConnectionListener-{p_state.connection_id}-InputStream')
        self._input_thread.start()
        

    def _byte_order_notation(self):
        return '<' if self._byte_order == 'little' else '>'
    
    def _read_data(self):
        '''
        This is running in a separate thread to read data from the socket
        '''
        while not self._input_thread_event.is_set():
            try:
                data = self._socket.recv(1024)
            except socket.timeout:
                continue
            if not data:
                continue
            with self._p_state.encryption_lock:
                if self._p_state.encrypted:
                    cipher: CipherContext = self._p_state.decrypt_cipher
                    data = cipher.update(data)
            logger.debug(f'Received {data}')
            with self._buffer_lock:
                new_buffer = ByteBuffer(byte_order='big')
                old_buffer_data = self._buffer.buffer.copy()[self._buffer.position:]
                new_buffer.wrap(old_buffer_data, auto_flip=False)
                new_buffer.write(data)
                new_buffer.flip()
                self._buffer = new_buffer
                self._available = self._buffer.buffer_size
    
    def available(self):
        with self._buffer_lock:
            return self._available
        
    def read(self, size: int):
        with self._buffer_lock:
            data = self._buffer.read(size)
            self._available = self._available - len(data)
            return data

    def close(self):
        self._input_thread_event.set()
        self._input_thread.join()

class ConnectionOutputStream:
    '''
    * There is no need to call close() for output stream
    '''
    def __init__(self, socket: socket.socket, byte_order='big'):
        self._byte_order = byte_order
        self._buffer = ByteBuffer(byte_order=self._byte_order)
        self._socket = socket
        self._output_thread_event = threading.Event()
        self._buffer_lock = threading.Lock()

    def _byte_order_notation(self):
        return '<' if self._byte_order == 'little' else '>'
    
    def write(self, data: bytes):
        with self._buffer_lock:
            self._buffer.write(data)
    
    def flush(self):
        with self._buffer_lock:
            self._buffer.flip()
            data = self._buffer.read(self._buffer.buffer_size)
            self._socket.send(data)
            self._buffer = ByteBuffer(byte_order=self._byte_order)

class MCPacketInputStream(ConnectionInputStream):
    def __init__(self, socket: socket.socket, p_state: PacketConnectionState):
        super().__init__(socket, p_state=p_state)
    
    def read_packet(self, p_state: PacketConnectionState) -> packet.ServerboundPacket:
        '''
        All client initiated packet flow is handled here !!!
        TODO: Implement all packet types <- IN PROGRESS
        TODO: Implement better error handling
        TODO:   
            The notchian server (but not client) rejects compressed packets smaller than the threshold. 
            Uncompressed packets exceeding the threshold, however, are accepted.

        Raises:
            ProtocolError: When an incoming packet is invalid in some way
            DataCorruptedError: When the incoming packet is corrupted at lower level
        '''
        # TODO: Implement timeout
        while self.available() == 0:
            pass
        length = self.read_varint()
        if length > self.available():
            logger.warning(f'Packet length {length} exceeds available data {self.available()}')
            self.read(length)
            return None
        content = self.read(length)

        # packets at this point maybe compressed <- FIXED: Compressed packets are handled in the packet class
        # never call self.read() beyond this point
        secured_packet = BufferedPacket(byte_order='big')
        secured_packet.wrap(content, auto_flip=True)
        
        ### Handshake ###
        if p_state.state == ConnectionState.HANDSHAKE:
            if secured_packet.read_varint() != 0x00:
                raise ProtocolError('Invalid packet id')
            try:
                handshaking_packet = s_handshake.SHandshake(
                    protocol_version=ProtocolVersion.from_protocol_version(secured_packet.read_varint()), 
                    server_address=secured_packet.read_utf8_string(256), 
                    server_port=secured_packet.read_uint16(), 
                    next_state=secured_packet.read_varint()
                )
            except Exception as e:
                raise DataCorruptedError(f'Error while reading handshake packet: {e}')
            return handshaking_packet

        ### Status ###
        elif p_state.state == ConnectionState.STATUS:
            id = secured_packet.read_varint()
            if id == 0x00: # Status Request
                return s_status.SStatusRequest()
            elif id == 0x01: # Status Ping
                payload = secured_packet.read_int64()
                return s_status.SPingRequest(payload)
            else:
                raise Exception('Invalid packet id')
        
        ### Login ###
        elif p_state.state == ConnectionState.LOGIN:
            id = secured_packet.read_varint()
            if id == 0x00: # Login Start
                return s_login.SLoginStart(
                    secured_packet.read_utf8_string(16), 
                    secured_packet.read_uuid()
                )
            elif id == 0x01: # Encryption Response
                shared_secret_length = secured_packet.read_varint()
                shared_secret = secured_packet.read(shared_secret_length)
                verify_token_length = secured_packet.read_varint()
                verify_token = secured_packet.read(verify_token_length)
                return s_login.SEncryptionResponse(shared_secret, verify_token)
            elif id == 0x02: # Login Plugin Response
                message_id = secured_packet.read_varint()
                successful = secured_packet.read_bool()
                payload = secured_packet.read(secured_packet.length() - secured_packet.pos())
                return s_login.SLoginPluginResponse(
                    message_id=message_id,
                    successful=successful,
                    data=payload
                )
            elif id == 0x03: # Login acknowledged
                return s_login.SLoginAcknowledged()
            else:
                raise Exception('Invalid packet id')
        
        ### Configuration ###
        elif p_state.state == ConnectionState.CONFIGURATION:
            id = secured_packet.read_varint()
            if id == 0x00: # Client Information
                return s_config.SClientInformation(
                    locale=secured_packet.read_utf8_string(16),
                    view_distance=secured_packet.read_int8(),
                    chat_mode=secured_packet.read_varint(),
                    chat_colors=secured_packet.read_bool(),
                    displayed_skin_parts=secured_packet.read_uint8(),
                    main_hand=secured_packet.read_varint(),
                    enable_text_filtering=secured_packet.read_bool(),
                    allow_server_listings=secured_packet.read_bool()
                )
            elif id == 0x02: # Plugin Message
                channel = secured_packet.read_utf8_string(32767)
                data = secured_packet.read(secured_packet.length() - secured_packet.pos())
                logger.debug(f'Plugin message received: {channel}')
                return s_config.SPluginMessage(channel, data)
            elif id == 0x03: # Finish Configuration Acknowledged
                return s_config.SFinishConfigurationAcknowledged()
            else:
                raise Exception(f'Not implemented: {id}')
        else:
            raise Exception('Invalid state')
    
    def read_varint(self):
        result = 0
        shift = 0
        while True:
            b = struct.unpack(f'{self._byte_order_notation()}B', self.read(1))[0]
            result |= (b & 127) << shift
            shift += 7
            if not b & 128:
                break
        return result
        
class MCPacketOutputStream(ConnectionOutputStream):

    def __init__(self, socket: socket.socket, p_state: PacketConnectionState):
        super().__init__(socket)
        self._p_state = p_state
        self._buffer = BufferedPacket(byte_order='big')

    def write_packet(self, packet: packet.ClientboundPacket):
        buffered_packet = packet.get_bytes(p_state=self._p_state)
        packet_length = buffered_packet.buffer_size
        packet_content = buffered_packet.read(packet_length)
        with self._p_state.encryption_lock:
            if self._p_state.encrypted:
                cipher: CipherContext = self._p_state.encrypt_cipher
                packet_content = cipher.update(packet_content)
        self.write(packet_content)