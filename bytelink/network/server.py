from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, cast

from bytelink.config import PROTOCOL_VERSION
from bytelink.exceptions import DisconnectError, MalformedPacketError, MalformedPacketState, ProcessingError, ReadError
from bytelink.network.connection import Connection
from bytelink.packets import read_packet, write_packet
from bytelink.packets.abc import ClientBoundPacket, ServerBoundPacket
from bytelink.packets.handshaking import Handshake
from bytelink.packets.ping import Ping, Pong

if TYPE_CHECKING:
    from typing_extensions import Self

log = logging.getLogger(__name__)


class BaseServer(ABC):
    def __init__(self, address: tuple[str, int], timeout: float):
        self.address = address
        self.timeout = timeout
        self._server: asyncio.Server = None  # type: ignore # Will be set later

    @classmethod
    async def create(cls, bind_address: tuple[str, int], timeout: float) -> Self:
        obj = cls(bind_address, timeout)
        server = await asyncio.start_server(obj._on_connect_callback, bind_address[0], bind_address[1])
        obj._server = server

        return obj

    async def __aenter__(self) -> Self:
        if self._server is None:
            raise ValueError("Server not set! (use Server.create when making class new instances)")
        await self._server.__aenter__()
        await self._server.start_serving()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self._server.__aexit__(*args, **kwargs)

    async def listen(self) -> None:
        """Start listening for connections until the server is closed."""
        async with self:
            await self._server.wait_closed()

    async def read_packet(self, client_conn: Connection) -> ServerBoundPacket:
        """Read incoming packet from the client connection."""
        packet = await read_packet(client_conn)

        if not isinstance(packet, ServerBoundPacket):
            raise MalformedPacketError(MalformedPacketState.UNEXPECTED_PACKET, packet=packet)

        return packet

    async def write_packet(self, client_conn: Connection, packet: ClientBoundPacket) -> None:
        """Send given packet to the client connection."""
        await write_packet(client_conn, packet)

    async def _on_connect_callback(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
    ) -> None:
        """This function is ran as a callback whenever a new client connects to the server."""
        client_conn = Connection(client_reader, client_writer, self.timeout)

        try:
            await self.on_connect(client_conn)
        except DisconnectError as exc:
            try:
                await self.on_close(client_conn, exc)
                return
            finally:
                client_conn.close()

        while True:
            try:
                await self._process_packet(client_conn)
            except DisconnectError as exc:
                try:
                    await self.on_close(client_conn, exc)
                    break
                finally:
                    client_conn.close()

    async def _process_packet(self, client_conn: Connection) -> None:
        """Listen for a single incoming packet from client and handle it."""
        try:
            packet = await self.read_packet(client_conn)
        except DisconnectError as exc:
            raise exc
        except Exception as exc:
            if isinstance(exc, MalformedPacketError) and exc.state is MalformedPacketState.NO_DATA:
                ioerr = cast(IOError, exc.ioerror)
                if ioerr.args[0] == "Server did not respond with any information.":
                    raise DisconnectError("Timed out")

            err = ReadError(exc, "Unexpected error while reading packet")
            await self.on_error(client_conn, err)
            return

        try:
            await self.on_packet(client_conn, packet)
        except DisconnectError as exc:
            raise exc
        except Exception as exc:
            err = ProcessingError(exc, "Unexpected error while processing packet")
            await self.on_error(client_conn, err)

    @abstractmethod
    async def on_connect(self, client_conn: Connection) -> None:
        """Event called on a new client connection to the server."""

    @abstractmethod
    async def on_error(self, client_conn: Connection, error: Union[ProcessingError, ReadError]) -> None:
        """Event called on error happening while listening or handling packets."""

    @abstractmethod
    async def on_close(self, client_conn: Connection, disconnect_exc: DisconnectError) -> None:
        """Event called right before client disconnection."""

    @abstractmethod
    async def on_packet(self, client_conn: Connection, packet: ServerBoundPacket) -> None:
        """Event called on receiving a packet from the client."""


class Server(BaseServer):
    async def process_handshake(self, client_conn: Connection) -> None:
        """Read and process a handshake packet, ensuring client is on the same protocol version."""
        log.debug(f"Listening for a handshake from {client_conn.address}...")

        try:
            packet = await self.read_packet(client_conn)
        except Exception as exc:
            log.warning(f"Client {client_conn.address} sent invalid handshake: {exc}")
            raise DisconnectError("Failed to read handshake packet")

        if not isinstance(packet, Handshake):
            log.warning(f"Client {client_conn.address} sent invalid handshake: Got {packet} instead")
            raise DisconnectError("First packet must be a handshake packet.")

        if packet.protocol_version != PROTOCOL_VERSION:
            log.warning(
                f"Client {client_conn.address} tried to connect with different protocol version"
                f" (server version={PROTOCOL_VERSION}, client version={packet.protocol_version})."
            )
            raise DisconnectError(f"Mismatched protocol versions, server version: {PROTOCOL_VERSION}")

        log.debug(f"Handshake with {client_conn.address} successful, protocol versions match")

    async def on_connect(self, client_conn: Connection) -> None:
        log.info(f"New connection from: {client_conn.address}")
        await self.process_handshake(client_conn)

    async def on_error(self, client_conn: Connection, exc: Union[ProcessingError, ReadError]) -> None:
        log.debug(f"Handling error: {exc!r}")

        if isinstance(exc, ReadError):
            log.warning(f"Error occurred when reading a packet from {client_conn.address}: {exc.exc!r}")
        elif isinstance(exc, ProcessingError):
            log.warning(f"Error occurred when processing a packet from {client_conn.address}: {exc.exc!r}")

        raise DisconnectError("...")

    async def on_close(self, client_conn: Connection, exc: DisconnectError) -> None:
        log.info(f"Closing connection from: {client_conn.address} - {exc.message}")

    async def on_packet(self, client_conn: Connection, packet: ServerBoundPacket) -> None:
        log.debug(f"Received a packet from {client_conn.address} - {packet}")

        if isinstance(packet, Ping):
            log.info(f"Ping requested by {client_conn.address}, sending pong")
            resp_packet = Pong(packet.token)
            await write_packet(client_conn, resp_packet)
        else:
            log.warning(f"Got unexpected packet from {client_conn.address} - {packet}")
            # raise DisconnectError("...")
