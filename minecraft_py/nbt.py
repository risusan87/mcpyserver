
from abc import ABC, abstractmethod
from io import BytesIO
from gzip import GzipFile

from networking.data_type import ByteBuffer

def read_nbt(payload: ByteBuffer, compressed: bool=True):
    """
    Factory function to create an NBT tag from its binary representation.
    This function should be used to parse the payload and return an instance of the appropriate NBT tag class.
    """
    if compressed:
        with GzipFile(fileobj=BytesIO(payload.buffer), mode='rb') as gz:
            decompressed_data = gz.read()
        payload = ByteBuffer().wrap(decompressed_data, auto_flip=True)
    tag_id = payload.read(1)[0]
    Tag = _tag_registry.get(tag_id)
    if Tag is None:
        raise ValueError(f"Unknown NBT tag ID: {tag_id}")
    return Tag.from_payload(payload)

def write_nbt(tag: 'NBTBase', compressed: bool=True) -> bytes:
    if compressed:
        data = tag.to_payload().buffer
        buffer = BytesIO()
        with GzipFile(fileobj=buffer, mode='wb') as gz:
            gz.write(data)
        return buffer.getvalue()
    return tag.to_payload().buffer

_tag_registry = {}

class NBTBase(ABC):

    def register_tag(tag_id: int):
        def wrapper(cls):
            _tag_registry[tag_id] = cls
            cls.nbt_tag_id = tag_id
            return cls
        return wrapper
    
    def __init__(self, name: str=None, value: any=None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.to_snbt()

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, value: any):
        """
        Set the value of the NBT tag.
        This method should validate the value and raise a ValueError if it is invalid.
        """
        try:
            self._check_value(value)
        except ValueError as e:
            raise ValueError(f"Invalid value for {self.__class__.__name__}: {e}")
        self._value = value

    @abstractmethod
    def _check_value(self, value: any):
        """
        Check if the value is valid for this NBT tag type.
        This method should raise a ValueError if the value is invalid.
        """
        pass
    
    @abstractmethod
    def to_snbt(self) -> str:
        """
        Convert the NBT tag to a string in SNBT (Stringified NBT) format.
        """
        pass

    @abstractmethod
    def to_payload(self) -> ByteBuffer:
        """
        Convert the NBT tag to its binary representation.
        """
        if self.value is None:
            raise ValueError("Tag value cannot be None to convert to payload")
        payload = ByteBuffer()
        name_bytes = self.name.encode('utf-8') if self.name else b''
        name_length = len(name_bytes).to_bytes(2, byteorder='big', signed=False)
        tag_id = self.nbt_tag_id
        payload.write(tag_id).write(name_length).write(name_bytes)
        return payload
    
    @classmethod
    @abstractmethod
    def from_payload(cls, payload: ByteBuffer) -> 'NBTBase':
        """
        Reads NBT payload.
        This does not include the tag ID.
        All tags other than TagEnd must call super().from_payload(payload) at the beginning of this overridden method.
        """
        name_length = int.from_bytes(payload.read(2), payload.byte_order, signed=False)
        name = payload.read(name_length).decode('utf-8')
        return cls(name=name)

@NBTBase.register_tag(0x00)
class TagEnd(NBTBase):
    """
    Represents the end of an NBT structure.
    This is a special tag that indicates the end of a compound or list.
    """
    def __init__(self, name=None):
        if name is not None:
            raise ValueError("TagEnd does not support a name")
        super().__init__(name)

    def _check_value(self, value: any):
        if value is not None:
            raise ValueError("TagEnd does not support a value")

    def to_snbt(self) -> str:
        return ''
    
    def to_payload(self) -> ByteBuffer:
        payload = ByteBuffer()
        payload.write(self.nbt_tag_id, auto_flip=True)
        return payload
    
    @classmethod
    def from_payload(cls, payload: bytes) -> 'TagEnd':
        return cls()

@NBTBase.register_tag(0x01) 
class TagByte(NBTBase):
    """
    Represents a byte NBT tag.
    """
    def __init__(self, name: str=None, value: int=None):
        super().__init__(name, value)
    
    def _check_value(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Byte value must be an integer")
        if value is not None and (value < -128 or value > 127):
            raise ValueError("Byte value must be between -128 and 127")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{self.value}b' if self.name else f'{self.value}b'
    
    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(self.value & 0xFF, auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagByte':
        tag = super().from_payload(payload)
        value = payload.read(1)[0]
        tag.value = value - 256 if value > 127 else value
        return tag

@NBTBase.register_tag(0x0A)
class TagCompound(NBTBase):
    """
    Represents a compound NBT tag.
    This tag can contain other NBT tags as its value.
    """
    def __init__(self, name: str=None, value: list=None):
        super().__init__(name, value if value is not None else [])
    
    def _check_value(self, value: list):
        if not isinstance(value, list):
            raise ValueError("Compound value must be a list")
    
    def to_snbt(self) -> str:
        snbt = ''
        if self.name:
            snbt = f'{self.name}:'
        snbt += '{'
        if self.value:
            _f = False
            for tag in self.value:
                if _f:
                    snbt += ','
                else:
                    _f = True
                snbt += tag.to_snbt()
        snbt += '}'
        return snbt
        



    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        for tag in self.value:
            payload.write(tag.to_payload().buffer)
        payload.write(TagEnd().to_payload().buffer, auto_flip=True)
        return payload
    
    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagCompound':
        tag = super().from_payload(payload)
        tag.value = []
        while True:
            next_tag = read_nbt(payload, compressed=False)
            if isinstance(next_tag, TagEnd):
                break
            tag.value.append(next_tag)
        return tag


            
    
