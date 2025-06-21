import struct
import uuid
import io

class ByteBuffer:

    def __init__(self, byte_order='big'):
        """Simple byte buffer backed by :class:`io.BytesIO`."""
        self.byte_order = byte_order
        self.buffer = io.BytesIO()
        self.position = 0
        self.buffer_size = 0
    
    def _byte_order_notation(self):
        return '<' if self.byte_order == 'little' else '>'
    
    def _shift_position(self, shift: int, read: bool):
        self.position += shift
        if not read:
            self.buffer_size += shift

    def wrap(self, data, auto_flip=False) -> 'ByteBuffer':
        if isinstance(data, ByteBuffer):
            raw = data.buffer.getvalue()
            if self.byte_order != data.byte_order:
                raw = raw[::-1]
        elif isinstance(data, (bytes, bytearray)):
            raw = bytes(data)
        else:
            raise TypeError('Unsupported data type')

        self.buffer = io.BytesIO(raw)
        self.buffer_size = len(raw)
        if auto_flip:
            self.position = 0
            self.buffer.seek(0)
        else:
            self.position = self.buffer_size
            self.buffer.seek(self.buffer_size)
        return self

    def flip(self):
        self.buffer.seek(0)
        self.position = 0

    def write(self, data: bytes, auto_flip=False):
        """Append ``data`` to the buffer."""
        self.buffer.seek(0, io.SEEK_END)
        self.buffer.write(data)
        self._shift_position(len(data), False)
        if auto_flip:
            self.flip()
    
    def read(self, size: int):
        """Read ``size`` bytes from the current position."""
        self.buffer.seek(self.position)
        data = self.buffer.read(size)
        self._shift_position(len(data), True)
        return bytearray(data)
    
    def pos(self):
        return self.position
    
    def length(self):
        return self.buffer_size

class BufferedPacket(ByteBuffer):
    '''
    TODO: ERROR HANDLING for read functions!!!! This is lower level of the protocol.
    '''

    def read_bool(self):
        return self.read(1)[0] != 0
    
    def read_int8(self):
        return struct.unpack(f'{self._byte_order_notation()}b', self.read(1))[0]
    
    def read_uint8(self):
        return struct.unpack(f'{self._byte_order_notation()}B', self.read(1))[0]
    
    def read_int16(self):
        return struct.unpack(f'{self._byte_order_notation()}h', self.read(2))[0]
    
    def read_uint16(self):
        return struct.unpack(f'{self._byte_order_notation()}H', self.read(2))[0]
    
    def read_int32(self):
        return struct.unpack(f'{self._byte_order_notation()}i', self.read(4))[0]
    
    def read_int64(self):
        return struct.unpack(f'{self._byte_order_notation()}q', self.read(8))[0]
    
    def read_float(self):
        return struct.unpack(f'{self._byte_order_notation()}f', self.read(4))[0]
    
    def read_double(self):
        return struct.unpack(f'{self._byte_order_notation()}d', self.read(8))[0]
    
    def read_varint(self):
        result = 0
        shift = 0
        while True:
            b = self.read_uint8()
            result |= (b & 127) << shift
            shift += 7
            if not b & 128:
                break
        return result
    
    def read_varlong(self):
        result = 0
        shift = 0
        while True:
            b = self.read_uint8()
            result |= (b & 127) << shift
            shift += 7
            if not b & 128:
                break
        return result

    def read_utf8_string(self, n: int) -> str:
        '''
        Reads a UTF-8 string prefixed by its size in bytes as a VarInt.
        Validates against UTF-16 code unit and byte length limits.
        '''
        if n > 32767:
            raise ValueError("Maximum n value is 32767.")


        byte_length = self.read_varint()
        if byte_length < 1 or byte_length > (n * 3) + 3:
            raise ValueError(f"Invalid encoded string size: {byte_length}. Must be between 1 and {(n * 3) + 3} bytes.")

        utf8_bytes = self.read(byte_length)
        string = utf8_bytes.decode('utf-8')

        # Validate the number of UTF-16 code units in the decoded string
        utf16_code_units = sum(1 + (ord(ch) > 0xFFFF) for ch in string)
        if utf16_code_units > n:
            raise ValueError(f"Decoded string exceeds maximum of {n} UTF-16 code units.")

        return string
    
    def read_uuid(self) -> uuid:
        uuid_bytes = self.read(16)
        return uuid.UUID(bytes=bytes(uuid_bytes))
    
    def write_bool(self, value: bool):
        if value == True:
            self.write_uint8(1)
        else:
            self.write_uint8(0)

    def write_int8(self, value: int):
        if value < -128 or value > 127:
            raise ValueError('Byte value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}b', value))
    
    def write_uint8(self, value: int):
        if value < 0 or value > 255:
            raise ValueError('Unsigned byte value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}B', value))
    
    def write_int16(self, value: int):
        if value < -32768 or value > 32767:
            raise ValueError('Short value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}h', value))
    
    def write_uint16(self, value: int):
        if value < 0 or value > 65535:
            raise ValueError('Unsigned short value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}H', value))
    
    def write_int32(self, value: int):
        if value < -2147483648 or value > 2147483647:
            raise ValueError('Int value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}i', value))
    
    def write_int64(self, value: int):
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError('Long value out of range')
        self.write(struct.pack(f'{self._byte_order_notation()}q', value))
    
    def write_float(self, value: float):
        self.write(struct.pack(f'{self._byte_order_notation()}f', value))
    
    def write_double(self, value: float):
        self.write(struct.pack(f'{self._byte_order_notation()}d', value))
    
    def write_varint(self, value: int):
        if value < -2147483648 or value > 2147483647:
            raise ValueError('Int value out of range')
        while True:
            if (value & -128) == 0:
                self.write_uint8(value)
                return
            self.write_uint8(value & 127 | 128)
            value = value >> 7
    
    def write_varlong(self, value: int):
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError('Long value out of range')
        while True:
            if (value & -128) == 0:
                self.write_uint8(value)
                return
            self.write_uint8(value & 127 | 128)
            value = value >> 7

    def write_utf8_string(self, string: str, n: int):
        if n > 32767:
            raise ValueError("Maximum length is 32767")
        
        utf16_code_units = sum(1 + (ord(ch) > 0xFFFF) for ch in string)
        if utf16_code_units > n:
            raise ValueError(f"String exceeds maximum of {n} UTF-16 code units.")

        utf8_bytes = string.encode('utf-8')
        byte_length = len(utf8_bytes)

        if byte_length > n * 3:
            raise ValueError(f"Encoded UTF-8 string exceeds {n * 3} bytes.")

        self.write_varint(byte_length)
        self.write(utf8_bytes)

    def write_uuid(self, uuid: uuid.UUID):
        self.write(uuid.bytes)
