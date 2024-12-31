import os
from threading import Lock

from networking.protocol import ConnectionState

# per connection packet state
class PacketConnectionState:
    def __init__(self):

        # Server level state
        self.online_mode = True
        self.server_id = None

        # Connection level state
        self.state = ConnectionState.HANDSHAKE
        self.compress_threshold = -1
        self.client_ip = None
        self.username = None
        self.unique_message_id = int.from_bytes(os.urandom(4), byteorder='big', signed=True)

        # Encryption
        self.encryption_lock = Lock()
        self.encrypted = False
        self.public_key = None
        self.private_key = None
        self.decrypt_cipher = None
        self.encrypt_cipher = None
        self.verify_token = None