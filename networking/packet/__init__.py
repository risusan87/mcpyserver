
import zlib
from abc import ABC, abstractmethod

from networking.data_type import BufferedPacket
from networking.packet.packet_connection import PacketConnectionState

'''
All packets including both serverbound and clientbound must have packet_id property.
All packets including both serverbound and clientbound must have packet_body method.
Server packets that require response back to client must have handle method.
'''

class Packet(ABC):
    
    @property
    @abstractmethod
    def packet_id(self) -> int:
        pass


class ServerboundPacket(Packet):

    @abstractmethod
    def handle(self, p_state: PacketConnectionState) -> 'ClientboundPacket':
        pass


class ClientboundPacket(Packet):

    @abstractmethod
    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        '''
        This is the packet data without packet id. 
        Refered as "Data" in the documentation.
        '''
        pass

    def get_bytes(self, p_state: PacketConnectionState, compression_threshold=-1) -> BufferedPacket:
        '''
        This is the final packet that will be sent to the client.
        Encrypt as required.
        '''
        packet_body = BufferedPacket(byte_order='big')
        packet_body.write_varint(self.packet_id)
        p = self.packet_body(p_state)
        packet_body.write(p.read(p.buffer_size))
        packet_body.flip()
        packet_body_length = packet_body.buffer_size
        pre_packet = BufferedPacket(byte_order='big')
        if compression_threshold == -1:
            # send as compression disabled
            pre_packet.write(packet_body.read(packet_body_length))
        elif packet_body_length < compression_threshold:
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