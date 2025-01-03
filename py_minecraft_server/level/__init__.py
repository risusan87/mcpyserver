
import zlib
import asyncio
from concurrent.futures import ProcessPoolExecutor

from core.io import ByteBuffer
from core.logger import logger
from py_minecraft_server.io import NBTReader
from py_minecraft_server.nbt import NBT

class Chunk:
    '''
    Smallest unit of the world representation.
    a chunk is a 16x16x256 block area.
    '''
    _chunks = {}

    def __init__(self, x, z, timestamp=0, chunk_data=None):
        self.x = x
        self.z = z
        self._timestamp = timestamp
        self._chunk_data = chunk_data

        # logical server
        self._load_level = 34

    
    def is_loaded(self) -> bool:
        '''
        Loaded stage returns 0 if the chunk is pre-loaded, and 1 if the chunk is fully loaded.
        '''
        return True if isinstance(self._chunk_data, NBT) else False
    
    def load(self):
        '''
        Final stage of loading the chunk.
        This will load the chunk nbt data into memory and therefore computationally expensive, thus should be called when and only when chunk is within valid range of player. 
        '''
        if not self._chunk_data:
            return
        buffer = ByteBuffer.wrap(self._chunk_data, auto_flip=True)
        length = int.from_bytes(buffer.get(0x04), byteorder='big', signed=True)
        # Compression type supports 3 types, but notchian format appears to only use 2 (= Zlib)
        compression_type = int.from_bytes(buffer.get(0x01), byteorder='big')
        chunk_nbt = None
        # TODO: Implement other compression types, but not necessary?
        if compression_type == 2:
            chunk_nbt = zlib.decompress(buffer.get(length - 1))
            reader = NBTReader(chunk_nbt)
            nbt = reader.next_nbt()
            self._chunk_data = nbt
    
    def save(self):
        '''
        Saves the chunk at memory level
        '''
        pass
    
    def ticket(self, load_level: int, ticket_type: str, time_to_live: int=None):
        '''
        Sends a ticket to the chunk to load it for logical server.
        ticket_type: One of 'player', 'forced', 'start', 'portal', 'dragon', 'post-teleport', 'unknown' and 'light'.
        '''
        pass


class Region:
    '''
    Region is a square of chunks, natively at size of 32x32.
    Notchian client stores this information as .mca files under world save folder location.
    '''
    _regison = {}

    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self._chunks = {}
    
    def load(region_coord: tuple = None, chunk_coord: tuple = None):
        '''
        First stage of loading chunks.
        This will pre-load the chunk from physical file as bytes of data.
        Each call will always be a 32 x 32 chunk region.
        To fully load chunks, call Chunk.load() method.
        Thread unsafe - Do not call this other than logical server thread.

        This method is typically computationally inexpensive, but may occupy memory.
        '''
        if region_coord:
            x, z = region_coord
        elif chunk_coord:
            x, z = chunk_coord
            x = x >> 5
            z = z >> 5
        region = Region(x, z)
        with open(f'/home/deck/wk/mcserverpy/resources/logs/r.{x}.{z}.mca', 'rb') as f:
            for i in range(1024):
                f.seek(i * 0x04)
                offset_byte = int.from_bytes(f.read(0x03), byteorder='big', signed=False) * 0x1000
                length_byte = int.from_bytes(f.read(0x01), byteorder='big', signed=False) * 0x1000
                f.seek(0x1000 + i * 0x04)
                timestamp = int.from_bytes(f.read(0x04), byteorder='big', signed=False)
                f.seek(offset_byte)
                chunk_data = f.read(length_byte)
                c = Chunk(x * 32 + i % 32, z * 32 + i // 32, timestamp, chunk_data)
                region._chunks[(c.x, c.z)] = c
        Region._regison[(x, z)] = region

    def unload(region_coord: tuple = None, chunk_coord: tuple = None):
        '''
        Attempts to unload the region to free memory.
        Thread unsafe - Do not call this other than logical server thread
        '''
        pass

    def get_chunk(x: int, z: int) -> 'Chunk':
        '''
        Returns None if the chunk is not loaded. If this is the case, call Region.load() method.
        '''
        chunk: Chunk = Region._regison.get((x >> 5, z >> 5))._chunks[(x, z)]
        if not chunk:
            return None
        return chunk

