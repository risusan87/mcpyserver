import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pyncraft.nbt import (
    TagByte,
    TagShort,
    TagInt,
    TagLong,
    TagFloat,
    TagDouble,
    TagString,
    TagIntArray,
    TagLongArray,
    TagByteArray,
    TagList,
    TagCompound,
    TagEnd,
    read_nbt,
    write_nbt,
)
from networking.data_type import ByteBuffer


def roundtrip(tag):
    payload = tag.to_payload()
    result = read_nbt(payload, compressed=False)
    return result


class TestPrimitiveTags:
    def test_tagbyte_roundtrip(self):
        original = TagByte(name="a", value=5)
        parsed = roundtrip(original)
        assert isinstance(parsed, TagByte)
        assert parsed.name == "a"
        assert parsed.value == 5

    def test_tagshort_roundtrip(self):
        original = TagShort(name="b", value=12345)
        parsed = roundtrip(original)
        assert isinstance(parsed, TagShort)
        assert parsed.name == "b"
        assert parsed.value == 12345

    @pytest.mark.parametrize("value", [128, -129, "x"])
    def test_tagbyte_invalid(self, value):
        with pytest.raises(ValueError):
            TagByte(name="bad", value=value)

    @pytest.mark.parametrize("value", [40000, -40000, "x"])
    def test_tagshort_invalid(self, value):
        with pytest.raises(ValueError):
            TagShort(name="bad", value=value)

    def test_to_snbt(self):
        assert TagByte(name="b", value=1).to_snbt() == "b:1b"
        assert TagShort(value=2).to_snbt() == "2s"

    def test_tagintarray_roundtrip(self):
        original = TagIntArray(name="ints", value=[1, 2, 3])
        parsed = roundtrip(original)
        assert isinstance(parsed, TagIntArray)
        assert parsed.name == "ints"
        assert parsed.value == [1, 2, 3]

    def test_taglongarray_roundtrip(self):
        original = TagLongArray(name="longs", value=[1, 2, 3])
        parsed = roundtrip(original)
        assert isinstance(parsed, TagLongArray)
        assert parsed.name == "longs"
        assert parsed.value == [1, 2, 3]


class TestArrayTags:
    def test_byte_array_roundtrip(self):
        original = TagByteArray(name="arr", value=[1, -2, 3])
        parsed = roundtrip(original)
        assert isinstance(parsed, TagByteArray)
        assert parsed.name == "arr"
        assert parsed.value == [1, -2, 3]

    @pytest.mark.parametrize("values", [[256], [-129], ["a"]])
    def test_byte_array_invalid(self, values):
        with pytest.raises(ValueError):
            TagByteArray(name="bad", value=values)


class TestCompoundTag:
    def test_compound_roundtrip(self):
        inner = [TagByte(name="x", value=1), TagShort(name="y", value=2)]
        original = TagCompound(name="root", value=inner)
        parsed = roundtrip(original)
        assert isinstance(parsed, TagCompound)
        assert parsed.name == "root"
        assert len(parsed.value) == 2
        assert isinstance(parsed.value[0], TagByte)
        assert parsed.value[0].value == 1
        assert isinstance(parsed.value[1], TagShort)
        assert parsed.value[1].value == 2

    def test_compound_to_snbt(self):
        tag = TagCompound(name="root", value=[TagByte(name="x", value=1)])
        assert tag.to_snbt() == "root:{x:1b}"


class TestListTag:
    def test_list_roundtrip(self):
        original = TagList(name="list", value=[TagByte(value=1), TagByte(value=2)])
        parsed = roundtrip(original)
        assert isinstance(parsed, TagList)
        assert parsed.name == "list"
        assert len(parsed.value) == 2
        assert parsed.value[0].value == 1
        assert parsed.value[1].value == 2

    def test_list_to_snbt(self):
        tag = TagList(name="nums", value=[TagByte(value=1), TagByte(value=2)])
        assert tag.to_snbt() == "nums:[1b,2b]"


class TestReadWriteNbt:
    def test_write_and_read_compressed(self):
        tag = TagByte(name="c", value=3)
        data = write_nbt(tag, compressed=True)
        buf = ByteBuffer().wrap(data, auto_flip=True)
        parsed = read_nbt(buf, compressed=True)
        assert isinstance(parsed, TagByte)
        assert parsed.value == 3


class TestEdgeCases:
    def test_tag_end_invalid(self):
        with pytest.raises(ValueError):
            TagEnd(name="bad")
        with pytest.raises(ValueError):
            t = TagEnd()
            t.value = 1

    def test_tagstring_roundtrip_and_escape(self):
        original = TagString(name="s", value='hello "mc"')
        parsed = roundtrip(original)
        assert isinstance(parsed, TagString)
        assert parsed.value == 'hello "mc"'
        assert parsed.to_snbt() == 's:"hello \\"mc\\""'

    def test_taglist_invalid_mixed_types(self):
        with pytest.raises(ValueError):
            TagList(value=[TagByte(value=1), TagShort(value=2)])

    def test_taglist_named_elements_invalid(self):
        with pytest.raises(ValueError):
            TagList(value=[TagByte(name="x", value=1)])

    def test_taglist_empty_roundtrip(self):
        tag = TagList(name="empty", value=[])
        parsed = roundtrip(tag)
        assert isinstance(parsed, TagList)
        assert parsed.value == []
        assert parsed.list_type is TagEnd

    def test_list_type_mismatch(self):
        with pytest.raises(ValueError):
            TagList(list_type=TagByte, value=[TagShort(value=1)])

    def test_compound_invalid_value(self):
        with pytest.raises(ValueError):
            TagCompound(name="bad", value="string")

    def test_compound_nested(self):
        inner = TagCompound(name="inner", value=[TagString(name="msg", value="hi")])
        root = TagCompound(name="root", value=[inner])
        parsed = roundtrip(root)
        assert isinstance(parsed.value[0], TagCompound)
        assert parsed.value[0].name == "inner"
        assert isinstance(parsed.value[0].value[0], TagString)
        assert parsed.value[0].value[0].value == "hi"

    def test_unknown_tag_id(self):
        buf = ByteBuffer()
        buf.write(0xFF).write(b"\x00\x00", auto_flip=True)
        with pytest.raises(ValueError):
            read_nbt(buf, compressed=False)

    def test_tag_int_boundaries(self):
        for val in (-2147483648, 2147483647):
            assert roundtrip(TagInt(name="i", value=val)).value == val

    def test_tag_long_boundaries(self):
        for val in (-9223372036854775808, 9223372036854775807):
            assert roundtrip(TagLong(name="l", value=val)).value == val

    def test_float_double_roundtrip(self):
        ftag = TagFloat(name="f", value=1.25)
        dtag = TagDouble(name="d", value=1.5)
        assert roundtrip(ftag).value == pytest.approx(1.25)
        assert roundtrip(dtag).value == pytest.approx(1.5)
