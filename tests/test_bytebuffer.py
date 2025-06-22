import unittest
from networking.data_type import ByteBuffer

class TestByteBuffer(unittest.TestCase):
    def test_write_and_read(self):
        buf = ByteBuffer()
        buf.write(b'abc')
        buf.flip()
        self.assertEqual(buf.read(3), bytearray(b'abc'))
        self.assertEqual(buf.pos(), 3)
        self.assertEqual(buf.length(), 3)

    def test_wrap_bytes_auto_flip(self):
        buf = ByteBuffer()
        buf.wrap(b'xyz', auto_flip=True)
        self.assertEqual(buf.read(3), bytearray(b'xyz'))
        self.assertEqual(buf.pos(), 3)
        self.assertEqual(buf.length(), 3)

    def test_wrap_bytebuffer_byte_order(self):
        little = ByteBuffer(byte_order='little')
        little.write(b'\x01\x02')
        little.flip()
        big = ByteBuffer(byte_order='big')
        big.wrap(little, auto_flip=True)
        # when wrapping buffers of different byte order, data should be reversed
        self.assertEqual(big.read(2), bytearray(b'\x02\x01'))

if __name__ == '__main__':
    unittest.main()
