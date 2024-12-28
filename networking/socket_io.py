
import socket
import threading
import struct

import networking.packet as packet
from networking.data_type import ByteBuffer, BufferedPacket
from logger import logger
from networking.protocol import ConnectionState, ProtocolVersion
from networking.exception import ProtocolError, DataCorruptedError

class ConnectionInputStream:
    def __init__(self, socket: socket.socket, byte_order='big'):
        self._byte_order = byte_order
        self._buffer = ByteBuffer(byte_order=self._byte_order)
        self._socket = socket
        self._input_thread_event = threading.Event()
        self._buffer_lock = threading.Lock()
        self._available = 0
        self._input_thread = threading.Thread(target=self._read_data)
        self._input_thread.start()

    def _byte_order_notation(self):
        return '<' if self._byte_order == 'little' else '>'
    
    def _read_data(self):
        while not self._input_thread_event.is_set():
            data = self._socket.recv(1024)
            if not data:
                continue
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
            data = self._buffer.read(self._buffer.buffer_size)
            self._socket.send(data)
            self._buffer.flip()

class MCPacketInputStream(ConnectionInputStream):
    def __init__(self, socket: socket.socket):
        super().__init__(socket)
        self._buffer = BufferedPacket(byte_order='big')
    
    def read_packet(self, state: ConnectionState, compress_threshold: int, encryption: bool) -> packet.ServerboundPacket:
        '''
        All packet flow is handled here
        TODO: Implement all packet types
        TODO: Implement better error handling
        TODO:   
            The Notchian server (but not client) rejects compressed packets smaller than the threshold. 
            Uncompressed packets exceeding the threshold, however, are accepted.

        Raises:
            ProtocolError: When an incoming packet is invalid in some way
            DataCorruptedError: When the incoming packet is corrupted at lower level
        '''
        state: ConnectionState = state
        length = self.read_varint()
        if length > self.available():
            logger.warning(f'Packet length {length} exceeds available data {self.available()}')
            self.read(length)
            return None
        content = self.read(length)
        self._buffer = BufferedPacket(byte_order='big')
        self._buffer.wrap(content, auto_flip=True)

        ### Handle start ###
        if state == ConnectionState.HANDSHAKE:
            if self.read_varint() != 0x00:
                raise ProtocolError('Invalid packet id')
            try:
                handshaking_packet = packet.SHandshake(
                    protocol_version=ProtocolVersion.from_protocol_version(self._buffer.read_varint()), 
                    server_address=self._buffer.read_utf8_string(256), 
                    server_port=self._buffer.read_uint16(), 
                    next_state=self._buffer.read_varint()
                    )
            except Exception as e:
                raise DataCorruptedError(f'Error while reading handshake packet: {e}')
            return handshaking_packet

        elif state == ConnectionState.STATUS:
            id = self.read_varint()
            if id == 0x00: # Status Request
                return packet.SStatusRequest()
            elif id == 0x01: # Status Ping
                pass
            else:
                raise Exception('Invalid packet id')
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

    def __init__(self, socket: socket.socket):
        super().__init__(socket)
        self._buffer = BufferedPacket(byte_order='big')

    def write_packet(self, packet: packet.ClientboundPacket, compression_threshold: int, encryption: str):
        packet_bytes = packet.get_bytes(compression_threshold=compression_threshold)
        if encryption:
            pass
        self._buffer.write_varint(packet_bytes.buffer_size)
        self._buffer.write_varint(packet.packet_id)
        self.write(packet_bytes.read(packet_bytes.buffer_size))