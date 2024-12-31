
import uuid

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from networking.packet import ClientboundPacket
from networking.packet.packet_connection import PacketConnectionState
from networking.data_type import BufferedPacket
from networking.mc_crypto import gen_rsa_key_pair, encode_public_key_der

# Very fancy!!!
####
# Login packets
###
class CDisconnect(ClientboundPacket):
    def __init__(self, reason: str):
        self.reason = reason

    @property
    def packet_id(self):
        return 0x00
    
    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        body = BufferedPacket()
        body.write_utf8_string(self.reason)
        body.flip()
        return body

class CEncryptionRequest(ClientboundPacket):
    def __init__(self, online_mode: bool, verify_token=bytes([0x12, 0x34, 0x56, 0x78]), server_id=''):
        self.server_id = server_id
        self.online_mode = online_mode
        self.private_key, self.public_key = gen_rsa_key_pair()
        self.verify_token = verify_token
    
    @property
    def packet_id(self):
        return 0x01
    
    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        with p_state.encryption_lock:
            p_state.private_key = self.private_key
            p_state.public_key = self.public_key
        p_state.server_id = self.server_id
        p_state.verify_token = self.verify_token
        public_der = encode_public_key_der(p_state.public_key)
        body = BufferedPacket()
        body.write_utf8_string(self.server_id, 20)
        body.write_varint(len(public_der))
        body.write(public_der)
        body.write_varint(len(self.verify_token))
        body.write(self.verify_token)
        body.write_bool(p_state.online_mode) # this was the imposter 
        body.flip()
        return body
    
    def get_private_key(self):
        return self.private_key

class CLoginSuccess(ClientboundPacket):
    def __init__(self, uuid: uuid.UUID, username: str, num_properties: int, value: str, signature: str):
        self._uuid = uuid
        self._username = username
        self._num_properties = num_properties
        self._value = value
        self._signature = signature

    @property
    def packet_id(self):
        return 0x02
    
    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        body = BufferedPacket()
        body.write_uuid(self._uuid)
        body.write_utf8_string(self._username, 16)
        body.write_varint(self._num_properties)
        body.write_utf8_string('texture', 32767)
        body.write_utf8_string(self._value, 32767)
        if self._signature:
            body.write_bool(True)
            body.write_utf8_string(self._signature, 32767)
        body.flip()
        return body

class CSetCompression(ClientboundPacket):
    pass

class CLoginPluginRequest(ClientboundPacket):
    pass

class CCookieRequestAtLogin(ClientboundPacket):
    pass
