
import abc
import struct

from core.buffer import ByteBuffer

class NBT(abc.ABC):
    def __init__(self, data=None):
        self._data = data

    @property
    def tag_id(self) -> int:
        pass

    @property
    def tag_name(self) -> str:
        pass

    @abc.abstractmethod
    def _serialize(self, buffer: ByteBuffer):
        pass
    
    def serialize(self) -> bytes:
        binary_tag_buffer = ByteBuffer(byte_order='big')
        binary_tag_buffer.write(struct.pack('>B', self.tag_id))
        self._serialize(binary_tag_buffer)
        binary_tag_buffer.flip()
        return bytes(binary_tag_buffer.read(binary_tag_buffer.length()))
    
    def load(data: bytes) -> 'NBT':
        binary_tag_buffer = ByteBuffer(byte_order='big')
        binary_tag_buffer.wrap(data, auto_flip=True)
        root: NBT = None
        while True:
            tag_id = struct.unpack('>b', binary_tag_buffer.read(1))[0]
            if tag_id == 0x00:
                break
            if tag_id == 0x0A:
                tag_name_length = struct.unpack('>H', binary_tag_buffer.read(2))[0]
                tag_name = None if tag_name_length == 0 else binary_tag_buffer.read(tag_name_length).decode('utf-8')
                tag = TagCompound(tag_name)
                while True:
                    remaining_data = bytes(binary_tag_buffer.read(binary_tag_buffer.length() - binary_tag_buffer.pos()))
                    tag = NBT.load(remaining_data)
                
                return tag
        return NBT(data)
    
class TagCompound(NBT):
    def __init__(self, tag_name: str):
        self._tag_name = tag_name
        self._tags = []

    @property
    def tag_id(self) -> int:
        return 0x0A
    
    @property
    def tag_name(self) -> str:
        if self._tag_name is None:
            return ''
        return self._tag_name

    def _serialize(self, buffer: ByteBuffer):
        tag_name_bytes = self.tag_name.encode('utf-8')
        buffer.write(struct.pack('>H', len(tag_name_bytes)))
        buffer.write(tag_name_bytes)
        for tag in self._tags:
            tag: NBT = tag
            buffer.write(tag.serialize())


    def get(self, key: str) -> NBT:
        for tag in self._tags:
            tag: NBT = tag
            if tag.tag_name == key:
                return tag