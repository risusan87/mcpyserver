
import json
from typing import List

from networking.packet import ClientboundPacket
from networking.protocol import ConnectionState, ProtocolVersion
from networking.data_type import BufferedPacket
from minecraft_py.player import PlayerMP

###
# packet departure
###
class CStatusResponse(ClientboundPacket):
    
    def __init__(self, version: ProtocolVersion, max_players: int, online_players: int, sample_players: List[PlayerMP], description: str, enforce_secure_chat: bool):
        # Modern notchain server (MC 1.7+, specifically 13w41a and above):
        # TODO: Support favicon
        self._response = {
            'version': {
                'name': version.to_mc_version(),
                'protocol': version.value
            },
            'players': {
                'max': max_players,
                'online': online_players,
                'sample': [{'name': player.get_name(), 'id': player.get_uuid() } for player in sample_players]
            },
            'description': {'text': description},
            'enforcesSecureChat': enforce_secure_chat
        }
        # TODO: Support legacy clients (MC 1.6, specifically 13w39b and below)

    @property
    def packet_id(self):
        return 0x00
    
    @property
    def next_connection_state(self):
        return ConnectionState.STATUS

    def _packet_body(self) -> BufferedPacket:
        packet_body = BufferedPacket(byte_order='big')
        packet_body.write_utf8_string(json.dumps(self._response), 32767)
        packet_body.flip()
        return packet_body
    
class CPongResponse(ClientboundPacket):

    def __init__(self, timestamp: int):
        self._timestamp = timestamp

    @property
    def packet_id(self):
        return 0x01

    @property
    def next_connection_state(self):
        return ConnectionState.CLOSE

    def _packet_body(self) -> BufferedPacket:
        packet = BufferedPacket(byte_order='big')
        packet.write_int64(self._timestamp)
        return packet