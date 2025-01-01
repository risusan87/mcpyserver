
from core.logger import logger
from networking.packet import ServerboundPacket
from networking.packet.packet_connection import PacketConnectionState
from networking.protocol import ConnectionState

###
# Server Bound Configuration
###
class SClientInformation(ServerboundPacket):
    def __init__(self, locale: str, view_distance: int, chat_mode: int, chat_colors: bool, displayed_skin_parts: int, main_hand: int, enable_text_filtering: bool, allow_server_listings: bool):
        self._locale = locale
        self._view_distance = view_distance
        self._chat_mode = chat_mode
        self._chat_colors = chat_colors
        self._displayed_skin_parts = displayed_skin_parts
        self._main_hand = main_hand
        self._enable_text_filtering = enable_text_filtering
        self._allow_server_listings = allow_server_listings

    @property
    def packet_id(self):
        return 0x00
    
    def handle(self, p_state: PacketConnectionState) -> None:
        with p_state.client_information_lock:
            p_state.client_information_config_ready = True
            p_state.client_information_locale = self._locale
            p_state.client_information_view_distance = self._view_distance
            p_state.client_information_chat_mode = self._chat_mode
            p_state.client_information_chat_colors = self._chat_colors
            p_state.client_information_displayed_skin_parts = self._displayed_skin_parts
            p_state.client_information_main_hand = self._main_hand
            p_state.client_information_enable_text_filtering = self._enable_text_filtering
            p_state.client_information_allow_server_listings = self._allow_server_listings
        logger.debug(f'Locale: {self._locale}')
        logger.debug(f'View Distance: {self._view_distance}')
        logger.debug(f'Chat Mode: {self._chat_mode}')
        logger.debug(f'Chat Colors: {self._chat_colors}')
        logger.debug(f'Displayed Skin Parts: {self._displayed_skin_parts}')
        logger.debug(f'Main Hand: {self._main_hand}')
        logger.debug(f'Enable Text Filtering: {self._enable_text_filtering}')
        logger.debug(f'Allow Server Listings: {self._allow_server_listings}')

        return None

class SCookieResponse(ServerboundPacket):
    pass

class SPluginMessage(ServerboundPacket):
    def __init__(self, channel: str, data: bytes):
        self._channel = channel
        self._data = data
    
    @property
    def packet_id(self):
        return 0x02
    
    def handle(self, p_state: PacketConnectionState) -> None:
        return None

class SFinishConfigurationAcknowledged(ServerboundPacket):
    @property
    def packet_id(self):
        return 0x03
    
    def handle(self, p_state: PacketConnectionState) -> None:
        p_state.state = ConnectionState.PLAY
        return None

class SKeepAlive(ServerboundPacket):
    pass

class SPongResponse(ServerboundPacket):
    pass

class SResourcePackResponse(ServerboundPacket):
    pass

class SKnownPacks(ServerboundPacket):
    pass