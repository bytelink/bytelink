from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, TYPE_CHECKING

from bytelink.protocol.buffer import Buffer

if TYPE_CHECKING:
    from typing_extensions import Self


class Packet(ABC):
    """Base class for all packets"""

    PACKET_ID: ClassVar[int]

    def __init__(self, *args, **kwargs):
        """Enforce PAKCET_ID being set for each instance of concrete packet classes."""
        cls = self.__class__
        if not hasattr(cls, "PACKET_ID"):
            raise TypeError(f"Can't instantiate abstract {cls.__name__} class without defining PACKET_ID variable.")
        return super().__init__(*args, **kwargs)

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Buffer) -> Self:
        """Construct a packet from a buffer of bytes."""
        raise NotImplementedError

    @abstractmethod
    def serialize(self) -> Buffer:
        """Deconstruct a packet and represent it as a buffer of bytes."""
        raise NotImplementedError


class ServerBoundPacket(Packet):
    """Packet bound to a server (client -> server)."""


class ClientBoundPacket(Packet):
    """Packet bound to a client (server -> client)."""
