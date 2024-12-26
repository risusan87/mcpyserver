
import networking.packet.client_bound.status as chandshake
from networking.packet import ServerboundPacket, ClientboundPacket
from networking.protocol import ProtocolVersion

class SStatusRequest(ServerboundPacket):

    @property
    def packet_id(self):
        return 0x00

    # TODO: Retrieve info from server logic
    def handle(self) -> ClientboundPacket:
        return chandshake.CStatusResponse(ProtocolVersion.MC_1_21_4, 20, 10, [], 'Hello world!', False)
    
class SPingRequest(ServerboundPacket):

    
    @property
    def packet_id(self):
        return 0x01