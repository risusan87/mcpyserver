
import abc
from enum import Enum

class NBT(abc.ABC):
    def __init__(self, tag_name:str, value=None):
        self._value = value
        self.tag_name = tag_name

    @property
    def tag_id(self) -> int:
        pass

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
    
    def __str__(self):
        return f'{self.get()}'

class CompoundTag(NBT):
    def __init__(self, tag_name: str):
        super().__init__(tag_name, None)
        self._elements = {}
    
    def get_by_name(self, key: str) -> NBT:
        return self._elements[key]

    def get_by_index(self, index: int) -> NBT:
        return self._elements[index]

    def set_element(self, value: NBT):
        if value.tag_name and value.tag_name in self._elements.keys():
                raise ValueError('Tag already exists')
        self._elements[value.tag_name] = value

    def get(self):
        return None
    
    def set(self, value: dict):
        pass

class TagEnd(NBT):
    def __init__(self):
        super().__init__(None)

    @property
    def tag_id(self) -> int:
        return 0x00
    
    def get(self):
        return None
    
    def set(self, value):
        raise ValueError('TagEnd cannot have a value')

class TagByte(NBT):
    def __init__(self, tag_name: str, value: int):
        if value < -128 or value > 127:
            raise ValueError('TagByte value must be between -128 and 127')
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x01
    
    def get(self) -> int:
        return super().get()

    def set(self, value: int):
        if value < -128 or value > 127:
            raise ValueError('TagByte value must be between -128 and 127')
        super().set(value)

class TagShort(NBT):
    def __init__(self, tag_name: str, value: int):
        if value < -32768 or value > 32767:
            raise ValueError('TagShort value must be between -32768 and 32767')
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x02
    
    def get(self) -> int:
        return super().get()

    def set(self, value: int):
        if value < -32768 or value > 32767:
            raise ValueError('TagShort value must be between -32768 and 32767')
        super().set(value)

class TagInt(NBT):
    def __init__(self, tag_name: str, value: int):
        if value < -2147483648 or value > 2147483647:
            raise ValueError('TagInt value must be between -2147483648 and 2147483647')
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x03
    
    def get(self) -> int:
        return super().get()

    def set(self, value: int):
        if value < -2147483648 or value > 2147483647:
            raise ValueError('TagInt value must be between -2147483648 and 2147483647')
        super().set(value)

class TagLong(NBT):
    def __init__(self, tag_name: str, value: int):
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError('TagLong value must be between -9223372036854775808 and 9223372036854775807')
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x04
    
    def get(self) -> int:
        return super().get()

    def set(self, value: int):
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError('TagLong value must be between -9223372036854775808 and 9223372036854775807')
        super().set(value)

class TagFloat(NBT):
    def __init__(self, tag_name: str, value: float):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x05
    
    def get(self) -> float:
        return super().get()

    def set(self, value: float):
        super().set(value)

class TagDouble(NBT):
    def __init__(self, tag_name: str, value: float):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x06
    
    def get(self) -> float:
        return super().get()

    def set(self, value: float):
        super().set(value)

class TagByteArray(NBT):
    def __init__(self, tag_name: str, value: bytes):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x07
    
    def get(self) -> bytes:
        return super().get()

    def set(self, value: bytes):
        super().set(value)
    
    def __str__(self):
        s = '['
        f = True
        for b in self.get():
            s += '' if f else ','
            if f:
                f = False
            s += f'{b}'
        s += ']'
        return s

class TagString(NBT):
    def __init__(self, tag_name: str, value: str):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x08
    
    def get(self) -> str:
        return super().get()

    def set(self, value: str):
        super().set(value)

    def __str__(self):
        return f'"{self.get()}"'

class TagList(CompoundTag):
    def __init__(self, tag_name: str, tag_type: int):
        super().__init__(tag_name)
        self._tag_type = tag_type
        self._elements = []
    
    @property
    def tag_type(self) -> int:
        return self._tag_type
    
    @property
    def tag_id(self) -> int:
        return 0x09
    
    def set_element(self, value):
        if value.tag_id != self._tag_type:
            raise ValueError('Invalid tag type')
        self._elements.append(value)

    def __str__(self):
        s = (f'"{self.tag_name}":' if self.tag_name else '') + '['
        f = True
        for element in self._elements:
            s += '' if f else ','
            if f:
                f = False
            s += f'{element}'
        s += ']'
        return s

class TagCompound(CompoundTag):
    def __init__(self, tag_name: str):
        super().__init__(tag_name)

    @property
    def tag_id(self) -> int:
        return 0x0A

    def __str__(self):
        s = (f'"{self.tag_name}":' if self.tag_name else '') + '{'
        f = True
        for _, element in self._elements.items():
            s += '' if f else ','
            if f:
                f = False
            s += f'{element}' if isinstance(element, CompoundTag) else f'"{element.tag_name}":{element}'
        s += '}'
        return s

class TagIntArray(NBT):
    def __init__(self, tag_name: str, value: list):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x0B
    
    def get(self) -> list:
        return super().get()

    def set(self, value: list):
        super().set(value)
        
    def __str__(self):
        s = '['
        f = True
        for element in self.get():
            s += '' if f else ','
            if f:
                f = False
            s += f'{element}'
        s += ']'
        return s

class TagLongArray(NBT):
    def __init__(self, tag_name: str, value: list):
        super().__init__(tag_name, value)
    
    @property
    def tag_id(self) -> int:
        return 0x0C
    
    def get(self) -> list:
        return super().get()

    def set(self, value: list):
        super().set(value)
    
    def __str__(self):
        s = '['
        f = True
        for element in self.get():
            s += '' if f else ','
            if f:
                f = False
            s += f'{element}'
        s += ']'
        return s

class DataVersion(Enum):
    '''
    As of January 2024, the latest release version of MC 1.21 has a data version of Pending.
    '''
    MC_1_20_5 = 3837
    MC_1_20_4 = 3700
    MC_1_20_3 = 3698
    MC_1_20_2 = 3578
        