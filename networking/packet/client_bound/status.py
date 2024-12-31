
import json
from typing import List

from networking.packet import ClientboundPacket
from networking.protocol import ConnectionState, ProtocolVersion
from networking.data_type import BufferedPacket
from networking.packet.packet_connection import PacketConnectionState
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
            'description': {'text': description}
        }
        # TODO: Support legacy clients (MC 1.6, specifically 13w39b and below)

    @property
    def packet_id(self):
        return 0x00

    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        p_state.state = ConnectionState.STATUS
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

    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        packet = BufferedPacket(byte_order='big')
        packet.write_int64(self._timestamp)
        packet.flip()
        return packet