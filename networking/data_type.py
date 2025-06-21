import struct
import uuid

class ByteBuffer:

    def __init__(self, byte_order='big'):
        """
        Parameters:
        byte_order (str): The byte order of the buffer. Can be either 'little' or 'big'. Defaults to 'big'.
        """
        self.buffer = bytearray()
        self.position = 0
        self.buffer_size = 0
        self.byte_order = byte_order
    
    def _byte_order_notation(self):
        return '<' if self.byte_order == 'little' else '>'
    
    def _shift_position(self, shift: int, read: bool):
        self.position += shift
        if not read:
            self.buffer_size += shift

    def wrap(self, data, auto_flip=False) -> 'ByteBuffer':
        if isinstance(data, bytes):
            self.buffer = bytearray(data)
        elif isinstance(data, bytearray):
            self.buffer = data.copy()
        elif isinstance(data, ByteBuffer):
            self.buffer = data.buffer.copy()
            if self.byte_order != data.byte_order:
                data.buffer.reverse()
        self.buffer_size = len(self.buffer)
        self.position = 0 if auto_flip else self.buffer_size - 1
        return self

    def flip(self):
        self.position = 0

    def write(self, data: bytes, auto_flip=False):
        '''
        Write always appends data at the end of the buffer.
        '''
        if self.byte_order == 'little':
            self.buffer.reverse()
        self.buffer.extend(data)
        if self.byte_order == 'little':
            self.buffer.reverse()
        self._shift_position(len(data), False)
        if auto_flip:
            self.flip()
    
    def read(self, size: int):
        """
        Read data is always immutable.
        """
        if self.byte_order == 'little':
            self.buffer.reverse()
        data = self.buffer[self.position:self.position + size].copy()
        if self.byte_order == 'little':
            self.buffer.reverse()
        self._shift_position(size, True)
        return data
    
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
            result |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        # convert from unsigned to signed 32-bit value
        if result & 0x80000000:
            result -= 0x100000000
        return result
    
    def read_varlong(self):
        result = 0
        shift = 0
        while True:
            b = self.read_uint8()
            result |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        if result & 0x8000000000000000:
            result -= 0x10000000000000000
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
        unsigned = value & 0xFFFFFFFF
        while True:
            temp = unsigned & 0x7F
            unsigned >>= 7
            if unsigned != 0:
                temp |= 0x80
            self.write_uint8(temp)
            if unsigned == 0:
                break
    
    def write_varlong(self, value: int):
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError('Long value out of range')
        unsigned = value & 0xFFFFFFFFFFFFFFFF
        while True:
            temp = unsigned & 0x7F
            unsigned >>= 7
            if unsigned != 0:
                temp |= 0x80
            self.write_uint8(temp)
            if unsigned == 0:
                break

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