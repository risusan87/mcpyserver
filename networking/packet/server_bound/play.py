
from networking.packet import ServerboundPacket

###
# Server Bound Configuration (This is a lot but not as much as the client bound play :D :D :D)
###
class SConfirmTeleportation(ServerboundPacket):
    pass

class SQueryBlockEntityTag(ServerboundPacket):
    pass

class SBundleItemSelected(ServerboundPacket):
    pass

class SChangeDifficulty(ServerboundPacket):
    pass

class SAcknowledgeMessage(ServerboundPacket):
    pass

class SChatCommand(ServerboundPacket):
    pass

class SSignedChatCommand(ServerboundPacket):
    pass

class SChatMessage(ServerboundPacket):
    pass

class SPlayerSession(ServerboundPacket):
    pass

class SChunkBatchReceived(ServerboundPacket):
    pass

class SClientStatus(ServerboundPacket):
    pass

class SClientTickEnd(ServerboundPacket):
    pass

class SClientInformation(ServerboundPacket):
    pass

class SCommandSuggestionsRequest(ServerboundPacket):
    pass

class SAcknowledgeConfiguration(ServerboundPacket):
    pass

class SClickContainerButton(ServerboundPacket):
    pass

class SClickContainer(ServerboundPacket):
    pass

class SCloseContainer(ServerboundPacket):
    pass

class SChangeContainerSlotState(ServerboundPacket):
    pass

class SCookieResponse(ServerboundPacket):
    pass

class SPluginMessage(ServerboundPacket):
    pass

class SDebugSampleSubscription(ServerboundPacket):
    pass

class SEditBook(ServerboundPacket):
    pass

class SQueryEntityTag(ServerboundPacket):
    pass

class SInteract(ServerboundPacket):
    pass

class SJigsawGenerate(ServerboundPacket):
    pass

class SKeepAlive(ServerboundPacket):
    pass

class SLockDifficulty(ServerboundPacket):
    pass

class SPlayerPosition(ServerboundPacket):
    pass

class SSetPlayerPositionRotation(ServerboundPacket):
    pass

class SSetPlayerRotation(ServerboundPacket):
    pass

class SSetPlayerMovementFlags(ServerboundPacket):
    pass

class SMoveVehicle(ServerboundPacket):
    pass

class SPaddleBoat(ServerboundPacket):
    pass

class SPickItemFromBlock(ServerboundPacket):
    pass

class SPickItemFromEntity(ServerboundPacket):
    pass

class SPingRequest(ServerboundPacket):
    pass

class SPlaceRecipe(ServerboundPacket):
    pass

class SPlayerAbilities(ServerboundPacket):
    pass

class SPlayerAction(ServerboundPacket):
    pass

class SPlayerCommand(ServerboundPacket):
    pass

class SPlayerInput(ServerboundPacket):
    pass

class SPlayerLoaded(ServerboundPacket):
    pass

class SPongResponse(ServerboundPacket):
    pass

class SChangeRecipeBookSettings(ServerboundPacket):
    pass

class SSetSeenRecipe(ServerboundPacket):
    pass

class SRenameItem(ServerboundPacket):
    pass

class SResourcePackResponse(ServerboundPacket):
    pass

class SSeenAdvancements(ServerboundPacket):
    pass

class SSelectTrade(ServerboundPacket):
    pass

class SSetBeaconEffect(ServerboundPacket):
    pass

class SSetHeldItem(ServerboundPacket):
    pass

class SProgramCommandBlock(ServerboundPacket):
    pass

class SProgramCommandBlockMinecart(ServerboundPacket):
    pass

class SSetCreativeModeSlot(ServerboundPacket):
    pass

class SProgramJigsawBlock(ServerboundPacket):
    pass

class SProgramStructureBlock(ServerboundPacket):
    pass

class SUpdateSign(ServerboundPacket):
    pass

class SSwingArm(ServerboundPacket):
    pass

class STeleportToEntity(ServerboundPacket):
    pass

class SUseItemOn(ServerboundPacket):
    pass

class SUseItem(ServerboundPacket):
    pass