from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from bytelink.config import PROTOCOL_VERSION
from bytelink.network.connection import Connection
from bytelink.packets import read_packet, write_packet
from bytelink.packets.handshaking import Handshake
from bytelink.packets.ping import Ping, Pong

if TYPE_CHECKING:
    from typing_extensions import Self


class Client:
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

    async def connect(self) -> None:
        print("Sending a handshake")
        packet = Handshake(PROTOCOL_VERSION)
        await write_packet(self.connection, packet)

        print("Sending ping request..")
        packet = Ping("myrandomtoken")
        await write_packet(self.connection, packet)
        resp_packet = await read_packet(self.connection)

        if not isinstance(resp_packet, Pong):
            raise Exception("...")

        print("Got pong!")
        if resp_packet.token != "myrandomtoken":
            raise Exception("not match")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        self.connection.close()
