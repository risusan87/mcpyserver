
import zlib
from abc import ABC, abstractmethod

from networking.data_type import BufferedPacket
from networking.protocol import ConnectionState
from networking.packet.packet_connection import PacketConnectionState

class Packet(ABC):
    
    @property
    @abstractmethod
    def packet_id(self) -> int:
        pass


class ServerboundPacket(Packet):

    @abstractmethod
    def handle(self, p_state: PacketConnectionState) -> ClientboundPacket:
        pass


class ClientboundPacket(Packet):

    @abstractmethod
    def packet_body(self) -> BufferedPacket:
        '''
        This is the packet data without packet id. 
        Refered as "Data" in the documentation.
        '''
        pass

    @property
    @abstractmethod
    def next_connection_state(self) -> ConnectionState:
        pass

    def get_bytes(self, compression_threshold=-1) -> BufferedPacket:
        '''
        This is the final packet that will be sent to the client.
        Encrypt as required.
        '''
        packet_body = BufferedPacket(byte_order='big')
        packet_body.write_varint(self.packet_id)
        packet_body.write(self.packet_body().read(self.packet_body().buffer_size))
        packet_body.flip()
        packet_body_length = packet_body.buffer_size
        pre_packet = BufferedPacket(byte_order='big')
        if compression_threshold == -1 or packet_body_length < compression_threshold:
            # send as uncompressed
            pre_packet.write_varint(0x00)
            pre_packet.write(packet_body.read(packet_body_length))
        elif packet_body_length >= compression_threshold:
            # send as compressed
            compressed_packet = zlib.compress(packet_body.read(packet_body_length))
            pre_packet.write_varint(packet_body_length)
            pre_packet.write(compressed_packet)
        packet = BufferedPacket(byte_order='big')
        packet.write_varint(pre_packet.buffer_size)
        pre_packet.flip()
        packet.write(pre_packet.read(pre_packet.buffer_size))
        packet.flip()
        return packet