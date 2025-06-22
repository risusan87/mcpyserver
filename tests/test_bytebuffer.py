import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from networking.data_type import BufferedPacket

@pytest.mark.parametrize('value', [0, 1, 127, 128, 255, 300, -1, -300, 2147483647, -2147483648])
def test_varint_roundtrip(value):
    buf = BufferedPacket()
    buf.write_varint(value)
    buf.flip()
    assert buf.read_varint() == value
