import uuid

import networking.packet.client_bound.login as login
from networking.packet import ServerboundPacket

###
# Server bound login packets
###
class SLoginStart(ServerboundPacket):
    '''
    UUID appears to be unused by the notchian server.
    '''
    def __init__(self, username: str, uuid: uuid.UUID):
        self._username = username
        self._uuid = uuid

    @property
    def packet_id(self):
        return 0x00
    
    def handle(online_mode=True) -> 'login.CEncryptionRequest':
        return login.CEncryptionRequest(online_mode=online_mode)
    

class SEncryptionResponse(ServerboundPacket):
    def __init__(self, shared_secret: bytes, verify_token: bytes):
        self.shared_secret = shared_secret
        self.verify_token = verify_token
    @property
    def packet_id(self):
        return 0x01
    
    def handle(private_key: bytes, online_mode=True) -> 'login.CLoginSuccess':
        
        return login.CLoginSuccess()

class SLoginPluginResponse(ServerboundPacket):
    pass

class SLoginAcknowledged(ServerboundPacket):
    pass

class SCookieResponse(ServerboundPacket):
    pass