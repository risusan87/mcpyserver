
import uuid
import requests

from core.logger import logger
import networking.packet.client_bound.login as login
from networking.packet import ServerboundPacket
from networking.packet.packet_connection import PacketConnectionState
from networking.protocol import ConnectionState
from networking.mc_crypto import decrypt_rsa, gen_ciphers, auth_hash, encode_public_key_der

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
    
    def handle(self, p_state: PacketConnectionState) -> login.CEncryptionRequest:
        p_state.username = self._username
        return login.CEncryptionRequest(online_mode=p_state.online_mode)
    

class SEncryptionResponse(ServerboundPacket):
    def __init__(self, shared_secret: bytes, verify_token: bytes):
        self.shared_secret = shared_secret
        self.verify_token = verify_token

    @property
    def packet_id(self):
        return 0x01
    
    def handle(self, p_state: PacketConnectionState) -> login.CLoginSuccess:
        # check RSA encryption is valid
        if p_state.verify_token != decrypt_rsa(bytes(self.verify_token), p_state.private_key):
            raise ValueError('Encrypted token mismatch')
        shared_secret = decrypt_rsa(bytes(self.shared_secret), p_state.private_key)
        encrypt_cipher, decrypt_cipher = gen_ciphers(shared_secret)
        # Switch to AES encryption
        with p_state.encryption_lock:
            p_state.encrypted = True # extremely important
            p_state.encrypt_cipher = encrypt_cipher
            p_state.decrypt_cipher = decrypt_cipher
        # TODO: Authenticate client if online mode <- done! (almost)
        if p_state.online_mode:
            login_hash = auth_hash(
                server_id=p_state.server_id, 
                shared_secret=shared_secret, 
                public_der=encode_public_key_der(p_state.public_key)
            )
            auth_endpoint = 'https://sessionserver.mojang.com/session/minecraft/hasJoined'
            # TODO: Implement this with ip (appears that client IPs within LAN = doesn't work)
            # TODO: Notchian server is configurable for the IP, which includes only `prevent-proxy-connections` is set to be true.
            response = requests.get(auth_endpoint, params={'username': p_state.username, 'serverId': login_hash})
            if response.status_code != 200:
                raise ValueError(f'Authentication failed: {response.status_code}')
            auth_response = response.json()
            authorized_id = uuid.UUID(auth_response['id'])
            username = auth_response['name']
            value = auth_response['properties'][0]['value']
            signature = None
            if 'signature' in auth_response['properties'][0]:
                signature = auth_response['properties'][0]['signature']
        # TODO: Implement offline mode authentication
        # Connections are encrypted at this point,
        # this should be automatically done by the packet output stream.
        return login.CLoginSuccess(
            uuid=authorized_id,
            username=username,
            num_properties=1,
            value=value,
            signature=signature
        )


class SLoginPluginResponse(ServerboundPacket):
    '''
    For custom server/client handshake
    Notchian client always responds with successful = False, indicates client hasn't understood the request
    S -> C: LoginPluginRequest
    C -> S: LoginPluginResponse (This)
    '''
    def __init__(self, message_id: int, successful: bool, data: bytes):
        self._message_id = message_id
        self._successful = successful
        self._data = data
    
    @property
    def packet_id(self):
        return 0x02
    
    def handle(self, p_state: PacketConnectionState) -> None:
        if p_state.unique_message_id != self._message_id:
            raise ValueError('Message ID mismatch')
        if not self._successful:
            logger.warning('Login plugin response at login state (id = 0x02) responded with unsuccessful. Aborting.')
            return None
        # TODO: Implement this for custom handshake, however this is not necessary for the notchian client.
        return None
    
    def get_data(self) -> bytes:
        '''
        Call handle() first before calling this method.
        '''
        return self._data

class SLoginAcknowledged(ServerboundPacket):
    @property
    def packet_id(self):
        return 0x03
    
    def handle(self, p_state: PacketConnectionState) -> None:
        p_state.state = ConnectionState.CONFIGURATION
        return None

class SCookieResponse(ServerboundPacket):
    def __init__(self, cookie_identifier: str, payload: bytes):
        self._cookie_identifier = cookie_identifier
        self._payload = payload

    @property
    def packet_id(self):
        return 0x04
    
    def handle(self, p_state: PacketConnectionState) -> None:
        return None
    
    def get_payload(self):
        '''
        handle() is NOT necessary to call before this method.
        '''
        if self._payload:
            return self._cookie_identifier, self._payload
        return None