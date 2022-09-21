from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, cast

from bytelink.config import PROTOCOL_VERSION
from bytelink.network.connection import Connection
from bytelink.network.server import DisconnectError, MalformedPacketError, MalformedPacketState
from bytelink.packets import read_packet, write_packet
from bytelink.packets.abc import ClientBoundPacket, ServerBoundPacket
from bytelink.packets.handshaking import Handshake
from bytelink.packets.ping import Ping, Pong

if TYPE_CHECKING:
    from typing_extensions import Self

log = logging.getLogger(__name__)


class BaseClient(ABC):
    def __init__(self, server_address: tuple[str, int], timeout: float, connection: Connection):
        self.address = server_address
        self.timeout = timeout
        self.connection = connection

    @classmethod
    async def create(cls, server_address: tuple[str, int], timeout: float) -> Self:
        conn = asyncio.open_connection(server_address[0], server_address[1])
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        connection = Connection(reader, writer, timeout)
        return cls(server_address, timeout, connection)

    async def __aenter__(self) -> Self:
        await self.on_connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[Exception]],
        exc_value: Optional[Exception],
        exc_traceback: Optional[str],
    ) -> None:
        await self.on_close(exc_value)
        self.connection.close()

    async def read_packet(self) -> ClientBoundPacket:
        """Read incoming packet from the server."""
        try:
            packet = await read_packet(self.connection)
        except MalformedPacketError as exc:
            if exc.state is MalformedPacketState.NO_DATA:
                ioerr = cast(IOError, exc.ioerror)
                if ioerr.args[0] == "Server did not respond with any information.":
                    raise DisconnectError("Timed out")
            raise exc

        if not isinstance(packet, ClientBoundPacket):
            raise MalformedPacketError(MalformedPacketState.UNEXPECTED_PACKET, packet=packet)

        return packet

    async def write_packet(self, packet: ServerBoundPacket) -> None:
        """Send given packet to the server."""
        await write_packet(self.connection, packet)

    @abstractmethod
    async def on_connect(self) -> None:
        """Event called on initial connection to the server."""

    @abstractmethod
    async def on_close(self, exc: Optional[Exception]) -> None:
        """Event called just before disconnection from the server."""


class Client(BaseClient):
    async def send_handshake(self, ping_token: str) -> None:
        log.debug(f"Sending a handshake to {self.address}...")

        packet = Handshake(PROTOCOL_VERSION)
        await self.write_packet(packet)

        log.debug("Sending a ping request")
        packet = Ping(ping_token)
        await self.write_packet(packet)
        resp_packet = await self.read_packet()

        log.debug("Verifying ping token")
        if not isinstance(resp_packet, Pong):
            log.error(f"Handshaking failed, server sent an unexpected ping response - {resp_packet}")
            raise DisconnectError("Got invalid ping token")
        if resp_packet.token != ping_token:
            log.error(f"Handshaking failed, server sent a mismatched ping token - {resp_packet.token} != {ping_token}")
            raise DisconnectError("Mismatched ping tokens")

        log.debug("Handshake with server successful.")

    async def on_connect(self) -> None:
        await self.send_handshake("abc")
        log.info("Connection with the server established")

    async def on_close(self, exc: Optional[Exception]) -> None:
        if exc is not None:
            log.error("Closing connection due to an exception!")
