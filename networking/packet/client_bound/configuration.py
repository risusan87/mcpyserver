
from networking.packet import ClientboundPacket
from networking.packet.packet_connection import PacketConnectionState
from networking.data_type import BufferedPacket

###
# Client bound configuration packets
###
class CCookieRequest(ClientboundPacket):
    pass

class CPluginMassage(ClientboundPacket):
    pass

class CDisconnect(ClientboundPacket):
    pass

class CFinishConfiguration(ClientboundPacket):
    @property
    def packet_id(self):
        return 0x03
    
    def packet_body(self, p_state: PacketConnectionState) -> BufferedPacket:
        return BufferedPacket()

class CKeepAlive(ClientboundPacket):
    pass

class CPing(ClientboundPacket):
    pass

class CResetChat(ClientboundPacket):
    pass

class CRegistryData(ClientboundPacket):
    pass

class CRemoveResourcePack(ClientboundPacket):
    pass

class CAddResourcePack(ClientboundPacket):
    pass

class CStoreCookie(ClientboundPacket):
    pass

class CTransfer(ClientboundPacket):
    pass

class CFeatureFlags(ClientboundPacket):
    '''
    As of 1.21, the following feature flags are available:
        - minecraft:vanilla - enables vanilla features
        - minecraft:bundle - enables support for the bundle
        - minecraft:trade_rebalance - enables support for the rebalanced villager trades
    '''
    pass

class CUpdateTags(ClientboundPacket):
    pass

class CKnownPacks(ClientboundPacket):
    pass

class CCustomReportDetails(ClientboundPacket):
    pass

class CServerLinks(ClientboundPacket):
    pass

