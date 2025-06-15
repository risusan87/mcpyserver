
from abc import ABC, abstractmethod

class NBTBase(ABC):

    nbt_tag_id: int

    @abstractmethod
    def to_snbt(self) -> str:
        """
        Convert the NBT tag to a string in SNBT (Stringified NBT) format.
        """
        pass

    @abstractmethod
    def to_nbt(self) -> bytes:
        """
        Convert the NBT tag to its binary representation.
        """
        pass

class DataNBT(NBTBase):
    """
    Represents a data NBT structure, such as String, Int, Float, etc.
    """
    @abstractmethod
    def to_data(self) -> any:
        """
        Convert the NBT tag to its native data type.
        For example, a String tag would return a Python string.
        """
        pass

class ArrayNBT(NBTBase):
    """
    Represents an array NBT structure, such as List or Compound.
    """
    pass

class NestedNBT(NBTBase):
    """
    Represents a nested NBT structure, such as Compound or NamedTag.
    """
    pass

class TagEnd(NBTBase):
    """
    Represents the end of an NBT structure.
    This is a special tag that indicates the end of a compound or list.
    """
    nbt_tag_id = 0x00

    def to_snbt(self) -> str:
        return None
    
    def to_nbt(self) -> bytes:
        return bytes(0)
    

class TagByte(DataNBT):
    """
    Represents a byte NBT tag.
    """
    nbt_tag_id = 0x01

class TagShort(DataNBT):
    """
    Represents a short NBT tag.
    """
    nbt_tag_id = 0x02

class TagInt(DataNBT):
    """
    Represents an int NBT tag.
    """
    nbt_tag_id = 0x03

class TagLong(DataNBT):
    """
    Represents a long NBT tag.
    """
    nbt_tag_id = 0x04

class TagFloat(DataNBT):
    """
    Represents a float NBT tag.
    """
    nbt_tag_id = 0x05

class TagDouble(DataNBT):
    """
    Represents a double NBT tag.
    """
    nbt_tag_id = 0x06

class TagByteArray(ArrayNBT):
    """
    Represents a byte array NBT tag.
    """
    nbt_tag_id = 0x07

class TagString(TagByteArray):
    """
    Represents a string NBT tag.
    """
    nbt_tag_id = 0x08

class TagList(ArrayNBT):
    """
    Represents a list NBT tag.
    """
    nbt_tag_id = 0x09

class TagCompound(NestedNBT):
    """
    Represents a compound NBT tag.
    This is a collection of key-value pairs where keys are strings and values can be any NBT type.
    """
    nbt_tag_id = 0x0A

class TagIntArray(ArrayNBT):
    """
    Represents an int array NBT tag.
    """
    nbt_tag_id = 0x0B

class TagLongArray(ArrayNBT):
    """
    Represents a long array NBT tag.
    """
    nbt_tag_id = 0x0C






    

