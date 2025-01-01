
from minecraft_py.level.chunk import Chunk

class Region:
    '''
    Region is a square of chunks, natively at size of 32x32.
    Notchian client stores this information as .mca files under world save folder locations.
    '''
    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self.chunks = []
    
    def load(self):
        '''
        Reads a region from a file based on defined x and y coordinates and loads it into memory.
        Thread unsafe - Do not call this other than logical server thread
        '''
        with open(f'/home/deck/wk/mcserverpy/resources/logs/r.{self.x}.{self.z}.mca', 'rb') as f:
            for i in range(1024):
                f.seek(i * 0x04)
                offset_byte = int.from_bytes(f.read(0x03), byteorder='big', signed=False) * 0x1000
                length_byte = int.from_bytes(f.read(0x01), byteorder='big', signed=False) * 0x1000
                f.seek(0x1000 + i * 0x04)
                timestamp = int.from_bytes(f.read(0x04), byteorder='big', signed=False)
                f.seek(offset_byte)
                chunk_data = f.read(length_byte)
                c = Chunk(self.x * 32 + i % 32, self.z * 32 + i // 32, timestamp, chunk_data)
                self.chunks.append(c)
        for c in self.chunks:
            c: Chunk = c
            c._digest()
        print(f'loaded {len(self.chunks)} chunks')
    
    def unload(self):
        '''
        Unloads the region to free memory.
        Thread unsafe - Do not call this other than logical server thread
        '''
        pass

