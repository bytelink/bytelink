from __future__ import annotations

import asyncio

from bytelink.config import Config
from bytelink.network.server import Server


async def main() -> None:
    server = await Server.create((Config.IP, Config.PORT), timeout=float("inf"))
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
