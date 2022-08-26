from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from zerocom.packets.abc import ServerBoundPacket
from zerocom.protocol.buffer import Buffer

if TYPE_CHECKING:
    from typing_extensions import Self


class Handshake(ServerBoundPacket):
    PACKET_ID: ClassVar[int] = 3

    def __init__(self, protocol_version: int):
        super().__init__()
        self.protocol_version = protocol_version

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_varint(self.protocol_version, max_bits=32)
        return buf

    @classmethod
    def deserialize(cls, data: Buffer) -> Self:
        protocol_version = data.read_varint(max_bits=32)
        return cls(protocol_version)
