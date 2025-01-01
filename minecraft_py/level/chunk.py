
import zlib

from core.buffer import ByteBuffer

class Chunk:
    '''
    Smallest unit of the world representation.
    a chunk is a 16x16x256 block area.
    '''
    def __init__(self, x, z, timestamp=0, chunk_data=None):
        self.x = x
        self.z = z
        self._timestamp = timestamp
        self._chunk_data = chunk_data
    
    def _digest(self):
        buffer = ByteBuffer(byte_order='big')
        buffer.wrap(self._chunk_data, auto_flip=True)
        length = int.from_bytes(buffer.read(0x04), byteorder='big', signed=True)
        # Compression type supports 3 types, but notchian format appears to only use 2 (= Zlib)
        compression_type = int.from_bytes(buffer.read(0x01), byteorder='big')
        chunk_nbt = None
        # TODO: Implement other compression types, but not necessary?
        if compression_type == 2:
            chunk_nbt = ByteBuffer(byte_order='big')
            chunk_nbt.wrap(zlib.decompress(buffer.read(length - 1)), auto_flip=True)
        if chunk_nbt:
            print(int.from_bytes(chunk_nbt.read(1), byteorder='big'))
        
        
        