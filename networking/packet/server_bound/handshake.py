
from networking.packet import ServerboundPacket, ClientboundPacket, CEmptyPacket
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
    
    def handle(self) -> ClientboundPacket:
        if self._next_state == 1:
            return CEmptyPacket(next_server_state=ConnectionState.STATUS)
        elif self._next_state == 2:
            return CEmptyPacket(next_server_state=ConnectionState.LOGIN)
        elif self._next_state == 3:
            return CEmptyPacket(next_server_state=ConnectionState.CONFIGURATION)
        else:
            raise ProtocolError('Invalid next state')