
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from networking.packet import ClientboundPacket
from networking.data_type import BufferedPacket

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
    
    def packet_body(self) -> BufferedPacket:
        body = BufferedPacket()
        body.write_utf8_string(self.reason)
        body.flip()
        return body

class CEncryptionRequest(ClientboundPacket):
    def __init__(self, online_mode: bool, verify_token=bytes(0x10203040), server_id=''):
        self.server_id = server_id
        self.online_mode = online_mode
        self.verify_token = verify_token
        private_key = rsa.generate_private_key(key_size=1024, public_exponent=65537)
        self.public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    @property
    def packet_id(self):
        return 0x01
    
    def packet_body(self) -> BufferedPacket:
        body = BufferedPacket()
        body.write_utf8_string(self.server_id, 20)
        body.write_varint(len(self.public_key))
        body.write(self.public_key)
        body.write_varint(len(self.verify_token))
        body.write(self.verify_token)
        body.write_bool(self.online_mode)
        body.flip()
        return body
    
    def get_private_key(self):
        return self.private_key

class CLoginSuccess(ClientboundPacket):
    pass

class CSetCompression(ClientboundPacket):
    pass

class CLoginPluginRequest(ClientboundPacket):
    pass

class CCookieRequestAtLogin(ClientboundPacket):
    pass
