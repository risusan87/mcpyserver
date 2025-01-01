import os
import threading

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
        self.connection_id = None

        ### Application level state ###

        # SConfiguration/0x00
        self.client_information_lock = threading.Lock()
        self.client_information_config_ready = False
        self.client_information_initial_config_flag = False
        self.client_information_locale = None
        self.client_information_view_distance = None
        self.client_information_chat_mode = None
        self.client_information_chat_colors = None
        self.client_information_displayed_skin_parts = None
        self.client_information_main_hand = None
        self.client_information_enable_text_filtering = None
        self.client_information_allow_server_listings = None

        # Encryption
        self.encryption_lock = threading.Lock()
        self.encrypted = False
        self.public_key = None
        self.private_key = None
        self.decrypt_cipher = None
        self.encrypt_cipher = None
        self.verify_token = None