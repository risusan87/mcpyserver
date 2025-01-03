
import copy

class ByteBuffer:

    def __init__(self, size: int):
        """
        Parameters:
        size (int): Size of buffer allocation.
        byte_order (str): The byte order of the buffer. Can be either 'little' or 'big'. Defaults to 'big'.
        """
        self._position = 0
        if size < 0:
            raise ValueError('Buffer size can not be negative')
        self._buffer = bytes([0x00] * size)
        self._buffer_size = size
        self._mark = -1
    
    def _byte_order_notation(self, byte_order):
        return '<' if byte_order == 'little' else '>'
    
    def _shift_position(self, shift: int):
        self._position += shift
    
    def wrap(data, auto_flip=False) -> 'ByteBuffer':
        '''
        Creates a completely new buffer object, with the same data content.
        Returning buffer object will have no reference to the original data.

        Parameters:
            data (bytes, bytearray, ByteBuffer): Data to wrap. Returning buffer object will have no reference to the original data.
        '''
        if isinstance(data, bytes):
            pass
        elif isinstance(data, bytearray):
            d: bytearray = data
            data = bytes(copy.deepcopy(d))
        elif isinstance(data, ByteBuffer):
            d: ByteBuffer = data
            data = d._buffer
        else:
            raise ValueError('Data must be of type bytes, bytearray or ByteBuffer')
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
        self._position = 0

    def put(self, data: bytes, auto_flip=False):
        '''
        Writes data at current position.
        '''
        if len(data) + self._position > self._buffer_size:
            raise ValueError('Index out of bounds')
        self._buffer = self._buffer[:self._position] + data + self._buffer[self._position + len(data):]
        if auto_flip:
            self.flip()

    def get(self, size: int) -> bytes:
        '''
        Reads data from current position.
        '''
        if size + self._position > self._buffer_size:
            raise ValueError('Buffer underflow')
        data = self._buffer[self._position:self._position + size]
        self._shift_position(size)
        return data
    
    def pos(self):
        '''
        Gets current position of the buffer.
        '''
        return self.position
    
    def seek(self, position: int):
        '''
        Sets current position of the buffer.
        '''
        if position < 0 or position >= self._buffer_size:
            raise ValueError('Illegal position')
        self._position = position
    
    def mark(self):
        '''
        Marks the current position of the buffer.
        '''
        self._mark = self._position
    
    def reset(self):
        '''
        Resets the position of the buffer to the marked position.
        '''
        if self._mark == -1:
            raise ValueError('Invalid mark: Mark not set')
        self._position = self._mark
    
    def rewind(self):
        '''
        Resets the position of the buffer to 0 and removes the mark.
        '''
        self._position = 0
        self._mark = -1
    
    def remaining(self) -> int:
        '''
        Returns the number of bytes remaining in the buffer.
        '''
        return self._buffer_size - self._position
    
    def capacity(self):
        '''
        Returns the allocated size of the buffer.
        '''
        return self._buffer_size
    