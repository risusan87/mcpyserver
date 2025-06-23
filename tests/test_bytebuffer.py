import pytest
from networking.data_type import ByteBuffer


def test_write_and_read():
    buf = ByteBuffer()
    buf.write(b'abc')
    buf.flip()
    assert buf.read(3) == bytearray(b'abc')
    assert buf.pos() == 3
    assert buf.length() == 3


def test_wrap_bytes_auto_flip():
    buf = ByteBuffer()
    buf.wrap(b'xyz', auto_flip=True)
    assert buf.read(3) == bytearray(b'xyz')
    assert buf.pos() == 3
    assert buf.length() == 3


def test_wrap_bytebuffer_byte_order():
    little = ByteBuffer(byte_order='little')
    little.write(b'\x01\x02')
    little.flip()
    big = ByteBuffer(byte_order='big')
    big.wrap(little, auto_flip=True)
    # when wrapping buffers of different byte order, data should be reversed
    assert big.read(2) == bytearray(b'\x02\x01')

