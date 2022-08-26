from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

from zerocom.exceptions import DisconnectError
from zerocom.network.connection import Connection
from zerocom.packets import read_packet, write_packet
from zerocom.packets.abc import ClientBoundPacket, Packet, ServerBoundPacket
from zerocom.packets.ping import Ping, Pong

if TYPE_CHECKING:
    from typing_extensions import Self


class Server:
    def __init__(self, address: tuple[str, int], timeout: float):
        self.address = address
        self.timeout = timeout
        self._server: asyncio.Server = None  # type: ignore # Will be set later

    @classmethod
    async def create(cls, bind_address: tuple[str, int], timeout: float) -> Self:
        obj = cls(bind_address, timeout)
        server = await asyncio.start_server(obj.on_connect, bind_address[0], bind_address[1])
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

    async def on_connect(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
        """Function called each time a new client is connected."""
        client_conn = Connection(client_reader, client_writer, self.timeout)

        while True:
            try:
                try:
                    packet = await read_packet(client_conn)
                except (IOError, asyncio.exceptions.TimeoutError) as exc:
                    await self.on_error(client_conn, exc)
                else:
                    await self.process_packet(client_conn, packet)
            except DisconnectError as exc:
                await self.on_close(client_conn, exc)
                break

    async def on_error(self, client: Connection, exc: Exception) -> None:
        print(f"Got exc: {exc!r}")
        raise DisconnectError("Failed to read packet")

    async def on_close(self, client: Connection, exc: DisconnectError) -> None:
        client.close()

    async def process_packet(self, client: Connection, packet: Packet) -> None:
        if isinstance(packet, ClientBoundPacket):
            raise DisconnectError("Client sent a client-bound packet to server")
        packet = cast(ServerBoundPacket, packet)
        print(f"Processing packet: {packet}")

        if isinstance(packet, Ping):
            resp_packet = Pong(packet.token)
            await write_packet(client, resp_packet)
