
from networking.packet import ClientboundPacket

###
# Client Bound Play (This is a lot!!!)
###
class CBundleDelimiter(ClientboundPacket):
    pass

class CSpawnEntity(ClientboundPacket):
    '''
    * Aside from experience orbs*
    '''
    pass

class CSpawnExperienceOrb(ClientboundPacket):
    '''
    There we go.
    '''
    pass

class CEntityAnimation(ClientboundPacket):
    pass

class CAwardStatistics(ClientboundPacket):
    '''
    Sent as a response to Client Status (id 1). 
    Will only send the changed values if previously requested.
    '''
    pass

class CBlockChangeAcknowledge(ClientboundPacket):
    '''
    Acknowledges a user-initiated block change.
    '''
    pass

class CSetBlockDestroyStage(ClientboundPacket):
    pass

class CBlockEntityData(ClientboundPacket):
    pass

class CBlockAction(ClientboundPacket):
    '''
    !!! This packet uses a block ID from the minecraft:block registry, not a block state. !!!
    '''
    pass

class CBlockUpdate(ClientboundPacket):
    '''
    !!!
        Changing a block in a chunk that is not loaded is not a stable action. 
        The Notchian client currently uses a shared empty chunk which is modified for all block changes in unloaded chunks; 
        while in 1.9 this chunk never renders in older versions the changed block will appear in all copies of the empty chunk.
        Servers should avoid sending block changes in unloaded chunks and clients should ignore such packets.
    !!!
    '''
    pass

class CBossBar(ClientboundPacket):
    pass

class CChangeDifficulty(ClientboundPacket):
    pass

class CChunkBatchFinished(ClientboundPacket):
    pass

class CChunkBatchStart(ClientboundPacket):
    pass

class CChunkBiome(ClientboundPacket):
    pass

class CClearTitles(ClientboundPacket):
    pass

class CCommandSuggestionsResponse(ClientboundPacket):
    pass

class CCommands(ClientboundPacket):
    pass

class CCloseContainer(ClientboundPacket):
    pass

class CSetContainerContent(ClientboundPacket):
    pass

class CSetContainerProperty(ClientboundPacket):
    pass

class CSetContainerSlot(ClientboundPacket):
    pass

class CCookieRequest(ClientboundPacket):
    pass

class CSetCooldown(ClientboundPacket):
    pass

class CChatSuggestions(ClientboundPacket):
    pass

class CPluginMessage(ClientboundPacket):
    pass

class CDamageEvent(ClientboundPacket):
    pass

class CDebugSample(ClientboundPacket):
    pass

class CDeleteMessage(ClientboundPacket):
    pass

class CDisconnect(ClientboundPacket):
    pass

class CDisguisedChatMessage(ClientboundPacket):
    pass

class CEntityEvent(ClientboundPacket):
    pass

class CTeleportEntity(ClientboundPacket):
    '''
    !!!
        The Mojang-specified name of this packet was changed in 1.21.2 from teleport_entity to entity_position_sync.
        There is a new teleport_entity, which this document more appropriately calls Synchronize Vehicle Position.
        That packet has a different function and will lead to confusing results if used in place of this one.
    !!!
    '''
    pass

class CExplosion(ClientboundPacket):
    pass

class CUnloadChunk(ClientboundPacket):
    pass

class CGameEvent(ClientboundPacket):
    pass

class COpenHorseScreen(ClientboundPacket):
    pass

class CHurtAnimation(ClientboundPacket):
    pass

class CInitializeWorldBorder(ClientboundPacket):
    pass

class CKeepAlive(ClientboundPacket):
    pass

class CChunkDataAndUpdateLight(ClientboundPacket):
    pass

class CWorldEvent(ClientboundPacket):
    pass

class CParticle(ClientboundPacket):
    pass

class CUpdateLight(ClientboundPacket):
    pass

class CLogin(ClientboundPacket):
    pass

class CMapData(ClientboundPacket):
    pass

class CMerchantOffers(ClientboundPacket):
    pass

class CUpdateEntityPosition(ClientboundPacket):
    pass

class CUpdateEntityPositionRotation(ClientboundPacket):
    pass

class CMoveMinecartAlongTrack(ClientboundPacket):
    pass

class CUpdateEntityRotation(ClientboundPacket):
    pass

class CMoveVehicle(ClientboundPacket):
    pass

class COpenBook(ClientboundPacket):
    pass

class COpenScreen(ClientboundPacket):
    pass

class COpenSignEditor(ClientboundPacket):
    pass

class CPingRequest(ClientboundPacket):
    pass

class CPongResponse(ClientboundPacket):
    pass

class CPlaceGhostRecipe(ClientboundPacket):
    pass

class CPlayerAbilities(ClientboundPacket):
    pass

class CPlayerChatMessage(ClientboundPacket):
    pass

class CEndCombat(ClientboundPacket):
    pass

class CEnterCombat(ClientboundPacket):
    pass

class CCombatDeath(ClientboundPacket):
    pass

class CPlayerInfoRemove(ClientboundPacket):
    pass

class CPlayerInfoUpdate(ClientboundPacket):
    pass

class CLookAt(ClientboundPacket):
    pass

class CSynchronizePlayerPosition(ClientboundPacket):
    pass

class CPlayerRotation(ClientboundPacket):
    pass

class CRecipeBookAdd(ClientboundPacket):
    pass

class CRecipeBookRemove(ClientboundPacket):
    pass

class CRecipeBookSettings(ClientboundPacket):
    pass

class CRemoveEntities(ClientboundPacket):
    pass

class CRemoveEntityEffect(ClientboundPacket):
    pass

class CResetScore(ClientboundPacket):
    pass

class CRemoveResourcePack(ClientboundPacket):
    pass

class CAddResourcePack(ClientboundPacket):
    pass

class CRespawn(ClientboundPacket):
    pass

class CSetHeadRotation(ClientboundPacket):
    pass

class CUpdateSectionBlocks(ClientboundPacket):
    pass

class CSelectAdvancementTab(ClientboundPacket):
    pass

class CServerData(ClientboundPacket):
    pass

class CSetActionBarText(ClientboundPacket):
    pass

class CSetBorderCenter(ClientboundPacket):
    pass

class CSetBorderLerpSize(ClientboundPacket):
    pass

class CSetBorderSize(ClientboundPacket):
    pass

class CSetBorderWarningDelay(ClientboundPacket):
    pass

class CSetBorderWarningDistance(ClientboundPacket):
    pass

class CSetCamera(ClientboundPacket):
    pass

class CSetCenterChunk(ClientboundPacket):
    pass

class CSetRenderDistance(ClientboundPacket):
    pass

class CSetCursorItem(ClientboundPacket):
    pass

class CSetDefaultSpawnPosition(ClientboundPacket):
    pass

class CDisplayObjective(ClientboundPacket):
    pass

class CSetEntityMetadata(ClientboundPacket):
    pass

class CLinkEntities(ClientboundPacket):
    pass

class CSetEntityVelocity(ClientboundPacket):
    pass

class CSetEquipment(ClientboundPacket):
    pass

class CSetExperience(ClientboundPacket):
    pass

class CSetHealth(ClientboundPacket):
    pass

class CSetHeldItem(ClientboundPacket):
    pass

class CUpdateObjectives(ClientboundPacket):
    pass

class CSetPassengers(ClientboundPacket):
    pass

class CSetPlayerInventorySlot(ClientboundPacket):
    pass

class CUpdateTeams(ClientboundPacket):
    pass

class CUpdateScore(ClientboundPacket):
    pass

class CSetSimulationDistance(ClientboundPacket):
    pass

class CSetSubtitleText(ClientboundPacket):
    pass

class CUpdateTime(ClientboundPacket):
    pass

class CSetTitleText(ClientboundPacket):
    pass

class CSetTitleAnimationTimes(ClientboundPacket):
    pass

class CEntitySoundEffect(ClientboundPacket):
    '''
    !!! Numeric sound effect IDs are liable to change between versions. !!!
    '''
    pass

class CSoundEffect(ClientboundPacket):
    '''
    !!! Numeric sound effect IDs are liable to change between versions. !!!
    '''
    pass

class CStartConfiguration(ClientboundPacket):
    pass

class CStopSound(ClientboundPacket):
    pass

class CStoreCookie(ClientboundPacket):
    pass

class CSystemChatMessage(ClientboundPacket):
    pass

class CSetTabListHeaderFooter(ClientboundPacket):
    pass

class CTagQueryResponse(ClientboundPacket):
    pass

class CPickupItem(ClientboundPacket):
    pass

class CSynchronizeVehiclePosition(ClientboundPacket):
    pass

class CSetTickingState(ClientboundPacket):
    pass

class CStepTick(ClientboundPacket):
    pass

class CTransfer(ClientboundPacket):
    pass

class CUpdateAdvancements(ClientboundPacket):
    pass

class CUpdateAttributes(ClientboundPacket):
    pass

class CEntityEffect(ClientboundPacket):
    pass

class CUpdateRecipes(ClientboundPacket):
    pass

class CUpdateTags(ClientboundPacket):
    pass

class CProjectilePower(ClientboundPacket):
    pass

class CCustomReportDetails(ClientboundPacket):
    pass

class CServerLinks(ClientboundPacket):
    pass

