
import copy

class ByteBuffer:

    def __init__(self, size: int):
        """
        Parameters:
        size (int): Size of buffer allocation.
        byte_order (str): The byte order of the buffer. Can be either 'little' or 'big'. Defaults to 'big'.
        """
        self._buffer = bytearray()
        self._position = 0
        if size < 0:
            raise ValueError('Buffer size can not be negative')
        self._buffer_size = size
    
    def _byte_order_notation(self, byte_order):
        return '<' if byte_order == 'little' else '>'
    
    def _shift_position(self, shift: int, read: bool):
        self.position += shift
        if not read:
            self.buffer_size += shift
    
    def wrap(data, auto_flip=False) -> 'ByteBuffer':
        '''
        Creates a completely new buffer object, with the same data content.
        Returning buffer object will have no reference to the original data.

        Parameters:
            data (bytes, bytearray, ByteBuffer): Data to wrap. Returning buffer object will have no reference to the original data.
        '''
        if isinstance(data, bytes):
            d: bytes = data
            data = bytearray(d)
        elif isinstance(data, bytearray):
            d: bytearray = data
            data = copy.deepcopy(d)
        elif isinstance(data, ByteBuffer):
            d: ByteBuffer = data
            data: bytearray = copy.deepcopy(d._buffer)
        b = ByteBuffer(len(data))
        b._buffer = data
        return b
    
    def copy(self) -> 'ByteBuffer':
        '''
        Creates a deep copy of this buffer object
        '''
        b = ByteBuffer.wrap(self._buffer)
        b._position = self._position
        return b

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
    