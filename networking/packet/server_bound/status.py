
import networking.packet.client_bound.status as chandshake
from networking.packet import ServerboundPacket, ClientboundPacket
from networking.protocol import ProtocolVersion
from networking.packet.packet_connection import PacketConnectionState
from networking.protocol import ConnectionState

class SStatusRequest(ServerboundPacket):

    @property
    def packet_id(self):
        return 0x00

    # TODO: Retrieve info from server logic
    def handle(self, p_state: PacketConnectionState) -> ClientboundPacket:
        return chandshake.CStatusResponse(ProtocolVersion.MC_1_21_4, 20, 10, [], 'Hello world!', False)
    
class SPingRequest(ServerboundPacket):

    def __init__(self, timestamp: int):
        self._timestamp = timestamp

    @property
    def packet_id(self):
        return 0x01
    
    def handle(self, p_state: PacketConnectionState) -> ClientboundPacket:
        p_state.state = ConnectionState.CLOSE
        return chandshake.CPongResponse(self._timestamp)