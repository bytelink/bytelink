from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, overload


class ZerocomError(Exception):
    ...


class DisconnectError(ZerocomError):
    def __init__(self, message: str = ""):
        self.message = message
        return super().__init__(message)


class MalformedPacketState(Enum):
    """Enum describing all possible states for a malformed packet."""

    MALFORMED_PACKET_DATA = "Failed to read packet data"
    UNRECOGNIZED_PACKET_ID = "Unknown packet id"
    MALFORMED_PACKET_BODY = "Failed to deserialize packet"


class MalformedPacketError(ZerocomError):
    """Exception representing an issue while receiving packet."""

    @overload
    def __init__(self, state: Literal[MalformedPacketState.MALFORMED_PACKET_DATA], *, ioerror: IOError):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.UNRECOGNIZED_PACKET_ID], *, packet_id: int):
        ...

    @overload
    def __init__(self, state: Literal[MalformedPacketState.MALFORMED_PACKET_BODY], *, ioerror: IOError, packet_id: int):
        ...

    def __init__(
        self,
        state: MalformedPacketState,
        *,
        ioerror: Optional[IOError] = None,
        packet_id: Optional[int] = None,
    ):
        self.state = state
        self.packet_id = packet_id
        self.ioerror = ioerror

        msg_tail = []
        if self.packet_id:
            msg_tail.append(f"Packet ID: {self.packet_id}")
        if self.ioerror:
            msg_tail.append(f"Underlying IOError data: {self.ioerror}")

        msg = self.state.value
        if len(msg_tail) > 0:
            msg += f" ({', '.join(msg_tail)})"

        self.msg = msg
        return super().__init__(msg)
