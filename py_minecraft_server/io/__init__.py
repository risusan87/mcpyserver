
import struct

from core.io import ByteBuffer
import py_minecraft_server.nbt as nbt

class NBTReader(ByteBuffer):
    def __init__(self, data: bytes):
        super().__init__(len(data))
        self._buffer = data

    def next_nbt(self, pre_tag_id=None) -> nbt.NBT:
        '''
        tag_id: Given tag_id if this call was recursive.
        '''
        tag_id = pre_tag_id
        tag_name_length = 0
        tag_name = None
        if not pre_tag_id:
            tag_id = struct.unpack(f'>b', self.get(1))[0]
        if tag_id == 0x00:
            return nbt.TagEnd()
        if not pre_tag_id:
            tag_name_length = struct.unpack('>H', self.get(2))[0]
            tag_name = None if tag_name_length == 0 else self.get(tag_name_length).decode('utf-8')
        if tag_id == 0x01:
            value = struct.unpack('>b', self.get(1))[0]
            return nbt.TagByte(tag_name, value)
        elif tag_id == 0x02:
            value = struct.unpack('>h', self.get(2))[0]
            return nbt.TagShort(tag_name, value)
        elif tag_id == 0x03:
            value = struct.unpack('>i', self.get(4))[0]
            return nbt.TagInt(tag_name, value)
        elif tag_id == 0x04:
            value = struct.unpack('>q', self.get(8))[0]
            return nbt.TagLong(tag_name, value)
        elif tag_id == 0x05:
            value = struct.unpack('>f', self.get(4))[0]
            return nbt.TagFloat(tag_name, value)
        elif tag_id == 0x06:
            value = struct.unpack('>d', self.get(8))[0]
            return nbt.TagDouble(tag_name, value)
        elif tag_id == 0x07:
            array_size = struct.unpack('>i', self.get(4))[0]
            byte_array = []
            for _ in range(array_size):
                byte_array.append(struct.unpack('>B', self.get(1))[0])
            return nbt.TagByteArray(tag_name, bytes(byte_array))
        elif tag_id == 0x08:
            string_length = struct.unpack('>H', self.get(2))[0]
            value = self.get(string_length).decode('utf-8')
            return nbt.TagString(tag_name, value)
        elif tag_id == 0x09:
            list_type = struct.unpack('>b', self.get(1))[0]
            list_size = struct.unpack('>i', self.get(4))[0]
            tag_list = nbt.TagList(tag_name, list_type)
            for _ in range(list_size):
                element = self.next_nbt(pre_tag_id=list_type)
                tag_list.set_element(element)
            return tag_list
        elif tag_id == 0x0A:
            tag = nbt.TagCompound(tag_name)
            while True:
                element = self.next_nbt()
                if isinstance(element, nbt.TagEnd):
                    break
                tag.set_element(element)
            return tag
        elif tag_id == 0x0B:
            array_size = struct.unpack('>i', self.get(4))[0]
            int_array = []
            for _ in range(array_size):
                int_array.append(struct.unpack('>i', self.get(4))[0])
            return nbt.TagIntArray(tag_name, int_array)
        elif tag_id == 0x0C:
            array_size = struct.unpack('>i', self.get(4))[0]
            long_array = []
            for _ in range(array_size):
                long_array.append(struct.unpack('>q', self.get(8))[0])
            return nbt.TagLongArray(tag_name, long_array)
        else:
            raise ValueError('Invalid tag type')