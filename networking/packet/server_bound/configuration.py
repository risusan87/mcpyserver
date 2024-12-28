
from networking.packet import ServerboundPacket

###
# Server Bound Configuration
###
class SClientInformation(ServerboundPacket):
    pass

class SCookieResponse(ServerboundPacket):
    pass

class SPluginMessage(ServerboundPacket):
    pass

class SFinishConfigurationAcknowledge(ServerboundPacket):
    pass

class SKeepAlive(ServerboundPacket):
    pass

class SPongResponse(ServerboundPacket):
    pass

class SResourcePackResponse(ServerboundPacket):
    pass

class SKnownPacks(ServerboundPacket):
    pass