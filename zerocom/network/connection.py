from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

from zerocom.protocol.base_io import BaseAsyncReader, BaseAsyncWriter

T_STREAMREADER = TypeVar("T_STREAMREADER", bound=asyncio.StreamReader)
T_STREAMWRITER = TypeVar("T_STREAMWRITER", bound=asyncio.StreamWriter)


class Connection(BaseAsyncReader, BaseAsyncWriter, Generic[T_STREAMREADER, T_STREAMWRITER]):
    """Asynchronous networked implementation for reader and writer over working over TCP."""

    def __init__(self, reader: T_STREAMREADER, writer: T_STREAMWRITER, timeout: float):
        self.reader = reader
        self.writer = writer
        self.timeout = timeout

    async def read(self, length: int) -> bytearray:
        result = bytearray()
        while len(result) < length:
            new = await asyncio.wait_for(self.reader.read(length - len(result)), timeout=self.timeout)
            if len(new) == 0:
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                raise IOError(
                    f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes)."
                    f" Partial obtained data: {result!r}"
                )
            result.extend(new)

        return result

    async def write(self, data: bytes) -> None:
        self.writer.write(data)

    def close(self) -> None:
        self.writer.close()