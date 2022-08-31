from __future__ import annotations

import asyncio

from zerocom.config import Config
from zerocom.network.server import Server


async def main() -> None:
    server = await Server.create((Config.IP, Config.PORT), timeout=float("inf"))
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
