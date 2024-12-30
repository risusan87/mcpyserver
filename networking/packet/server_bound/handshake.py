
from networking.packet import ServerboundPacket, ClientboundPacket
from networking.packet.packet_connection import PacketConnectionState
from networking.protocol import ConnectionState
from networking.exception import ProtocolError


###
# packet arrival
###
class SHandshake(ServerboundPacket):

    def __init__(self, protocol_version: int, server_address: str, server_port: int, next_state: int):
        self._protocol_version = protocol_version
        self._server_address = server_address
        self._server_port = server_port
        self._next_state = next_state

    @property
    def packet_id(self):
        return 0x00
    
    def handle(self, p_state: PacketConnectionState) -> None:
        if self._next_state == 1:
            p_state.state = ConnectionState.STATUS
        elif self._next_state == 2:
            p_state.state = ConnectionState.LOGIN
        elif self._next_state == 3:
            p_state.state = ConnectionState.CONFIGURATION
        else:
            raise ProtocolError('Invalid next state')
        return None