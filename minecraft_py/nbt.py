
from abc import ABC, abstractmethod
from io import BytesIO
from gzip import GzipFile
import struct

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
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Byte value must be an integer")
            if value < -128 or value > 127:
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

@NBTBase.register_tag(0x02)
class TagShort(NBTBase):
    """
    Represents a short NBT tag.
    """
    def __init__(self, name: str=None, value: int=None):
        super().__init__(name, value)

    def _check_value(self, value: int):
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Short value must be an integer")
            if value < -32768 or value > 32767:
                raise ValueError("Short value must be between -32768 and 32767")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{self.value}s' if self.name else f'{self.value}s'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(self.value.to_bytes(2, byteorder='big', signed=True), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagShort':
        tag = super().from_payload(payload)
        tag.value = int.from_bytes(payload.read(2), payload.byte_order, signed=True)
        return tag

@NBTBase.register_tag(0x03)
class TagInt(NBTBase):
    """Represents a 32-bit signed integer NBT tag."""

    def __init__(self, name: str=None, value: int=None):
        super().__init__(name, value)

    def _check_value(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Int value must be an integer")
        if value is not None and (value < -2147483648 or value > 2147483647):
            raise ValueError("Int value must be between -2147483648 and 2147483647")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{self.value}i' if self.name else f'{self.value}i'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(self.value.to_bytes(4, byteorder='big', signed=True), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagInt':
        tag = super().from_payload(payload)
        tag.value = int.from_bytes(payload.read(4), byteorder='big', signed=True)
        return tag

@NBTBase.register_tag(0x04)
class TagLong(NBTBase):
    """Represents a 64-bit signed integer NBT tag."""

    def __init__(self, name: str = None, value: int = None):
        super().__init__(name, value)

    def _check_value(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Long value must be an integer")
        if value is not None and (value < -9223372036854775808 or value > 9223372036854775807):
            raise ValueError("Long value must be between -9223372036854775808 and 9223372036854775807")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{self.value}L' if self.name else f'{self.value}L'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(self.value.to_bytes(8, byteorder='big', signed=True), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagLong':
        tag = super().from_payload(payload)
        tag.value = int.from_bytes(payload.read(8), byteorder=payload.byte_order, signed=True)
        return tag
    
@NBTBase.register_tag(0x05)
class TagFloat(NBTBase):
    """
    Represents a float NBT tag.
    """

    def __init__(self, name: str=None, value: float=None):
        super().__init__(name, value)

    def _check_value(self, value: float):
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError("Float value must be a numeric type")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{float(self.value)}f' if self.name else f'{float(self.value)}f'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(struct.pack(f'{payload._byte_order_notation()}f', float(self.value)), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagFloat':
        tag = super().from_payload(payload)
        tag.value = struct.unpack(f'{payload._byte_order_notation()}f', payload.read(4))[0]
        return tag

@NBTBase.register_tag(0x06)
class TagDouble(NBTBase):
    """Represents a double precision floating point NBT tag."""

    def __init__(self, name: str = None, value: float = None):
        super().__init__(name, value)

    def _check_value(self, value: float):
        if value is None:
            return
        if not isinstance(value, (int, float)):
            raise ValueError("Double value must be a float")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        return f'{self.name}:{float(self.value)}d' if self.name else f'{float(self.value)}d'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(struct.pack('>d', float(self.value)), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagDouble':
        tag = super().from_payload(payload)
        tag.value = struct.unpack('>d', payload.read(8))[0]
        return tag

@NBTBase.register_tag(0x07)
class TagByteArray(NBTBase):
    """Represents a byte array NBT tag."""

    def __init__(self, name: str=None, value: list=None):
        super().__init__(name, value if value is not None else [])

    def _check_value(self, value: list):
        if not isinstance(value, list):
            raise ValueError("ByteArray value must be a list")
        for b in value:
            if not isinstance(b, int):
                raise ValueError("ByteArray elements must be integers")
            if b < -128 or b > 127:
                raise ValueError("ByteArray elements must be between -128 and 127")

    def to_snbt(self) -> str:
        snbt = ''
        if self.name:
            snbt = f'{self.name}:'
        values = ','.join(f'{b}b' for b in self.value)
        snbt += f'[B;{values}]'
        return snbt

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        payload.write(len(self.value).to_bytes(4, byteorder=payload.byte_order, signed=True))
        payload.write(bytes((b & 0xFF for b in self.value)), auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagByteArray':
        tag = super().from_payload(payload)
        length = int.from_bytes(payload.read(4), payload.byte_order, signed=True)
        data = payload.read(length)
        tag.value = [b - 256 if b > 127 else b for b in data]
        return tag

@NBTBase.register_tag(0x08)
class TagString(NBTBase):
    """Represents a string NBT tag."""

    def __init__(self, name: str = None, value: str = None):
        super().__init__(name, value)

    def _check_value(self, value: str):
        if value is not None and not isinstance(value, str):
            raise ValueError("String value must be a string")

    def to_snbt(self) -> str:
        if self.value is None:
            return None
        escaped = self.value.replace('"', '\\"')
        return f'{self.name}:"{escaped}"' if self.name else f'"{escaped}"'

    def to_payload(self) -> ByteBuffer:
        payload = super().to_payload()
        value_bytes = self.value.encode('utf-8')
        length = len(value_bytes).to_bytes(2, byteorder='big', signed=False)
        payload.write(length)
        payload.write(value_bytes, auto_flip=True)
        return payload

    @classmethod
    def from_payload(cls, payload: ByteBuffer) -> 'TagString':
        tag = super().from_payload(payload)
        length = int.from_bytes(payload.read(2), payload.byte_order, signed=False)
        tag.value = payload.read(length).decode('utf-8')
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


            
    
