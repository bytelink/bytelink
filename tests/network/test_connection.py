from __future__ import annotations

import asyncio
from typing import Optional
from unittest.mock import MagicMock

import pytest

from tests.protocol.helpers import ReadFunctionMock, WriteFunctionMock
from zerocom.network.connection import Connection


class MockReader(MagicMock):
    spec_set = asyncio.StreamReader

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kw) -> None:
        super().__init__(*args, **kw)
        self.read_f_mock = ReadFunctionMock(combined_data=read_data)

    async def read(self, *a, **kw):
        """Override read function of StreamReader to use the read mock."""
        return self.read_f_mock(*a, **kw)


class MockWriter(MagicMock):
    spec_set = asyncio.StreamWriter

    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.write_f_mock = WriteFunctionMock()

    def write(self, *a, **kw):
        """Override the write function of StreamWriter to use the write mock."""
        self.write_f_mock(*a, **kw)


async def test_read():
    data = bytearray("hello", "utf-8")
    conn = Connection(MockReader(read_data=data.copy()), MockWriter(), timeout=3)

    out = await conn.read(5)

    conn.reader.read_f_mock.recv.assert_read_everything()
    assert out == data


async def test_read_more_data_than_sent():
    conn = Connection(MockReader(read_data=bytearray("test", "utf-8")), MockWriter(), timeout=3)
    with pytest.raises(IOError):
        await conn.read(10)


async def test_write():
    data = bytearray("hello", "utf-8")
    conn = Connection(MockReader(), MockWriter(), timeout=3)

    await conn.write(data)

    conn.writer.write_f_mock.assert_has_data(data)
