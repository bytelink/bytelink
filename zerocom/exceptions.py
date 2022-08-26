from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, TYPE_CHECKING, overload

if TYPE_CHECKING:
    from zerocom.packets.abc import Packet


class ZerocomError(Exception):
    ...


class _WrapperError(ZerocomError):
    """Represent an arbitrary exception that wraps another exception."""

    def __init__(self, exc: Exception, msg: str = ""):
        self.exc = exc
        super().__init__(msg)


class ReadError(_WrapperError):
    """Represents an arbitrary exception which occurred while reading data."""


class ProcessingError(_WrapperError):
    """Represents an arbitrary exception which occurred while processing data."""


class DisconnectError(ZerocomError):
    def __init__(self, message: str = ""):
        self.message = message
        return super().__init__(message)


class MalformedPacketState(Enum):
    """Enum describing all possible states for a malformed packet."""

    NO_DATA = "No data were received"
    MALFORMED_PACKET_DATA = "Failed to read packet data"
    UNRECOGNIZED_PACKET_ID = "Unknown packet id"
    MALFORMED_PACKET_BODY = "Failed to deserialize packet"
    UNEXPECTED_PACKET = "This packet type was not expected"


class MalformedPacketError(ZerocomError):
    """Exception representing an issue while receiving packet."""

    @overload
    def __init__(self, state: Literal[MalformedPacketState.NO_DATA], *, ioerror: IOError):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.MALFORMED_PACKET_DATA], *, ioerror: IOError):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.UNRECOGNIZED_PACKET_ID], *, packet_id: int):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.MALFORMED_PACKET_BODY], *, ioerror: IOError, packet_id: int):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.UNEXPECTED_PACKET], *, packet: Packet):
        ...

    def __init__(
        self,
        state: MalformedPacketState,
        *,
        ioerror: Optional[IOError] = None,
        packet_id: Optional[int] = None,
        packet: Optional[Packet] = None,
    ):
        self.state = state

        self.packet = packet
        self.packet_id = packet_id if not packet else packet.PACKET_ID
        self.ioerror = ioerror

        msg_tail = []
        if self.packet_id:
            msg_tail.append(f"Packet ID: {self.packet_id}")
        if self.ioerror:
            msg_tail.append(f"Underlying IOError data: {self.ioerror!r}")
        if self.packet:
            msg_tail.append(f"Packet: {self.packet}")

        msg = self.state.value
        if len(msg_tail) > 0:
            msg += f" ({', '.join(msg_tail)})"

        self.msg = msg
        return super().__init__(msg)
