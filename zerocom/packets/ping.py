from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from zerocom.packets.abc import ClientBoundPacket, Packet, ServerBoundPacket
from zerocom.protocol.buffer import Buffer

if TYPE_CHECKING:
    from typing_extensions import Self


class _BasePing(Packet):
    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_utf(self.token)
        return buf

    @classmethod
    def deserialize(cls, data: Buffer) -> Self:
        token = data.read_utf()
        return cls(token)


class Ping(_BasePing, ServerBoundPacket):
    """Ping request packet."""

    PACKET_ID: ClassVar[int] = 1


class Pong(_BasePing, ClientBoundPacket):
    """Ping response packet."""

    PACKET_ID: ClassVar[int] = 2
