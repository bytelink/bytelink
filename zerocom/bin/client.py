from __future__ import annotations

import asyncio

from zerocom.config import Config
from zerocom.network.client import Client


async def main() -> None:
    client = await Client.create((Config.IP, Config.PORT), timeout=3)

    async with client:
        await client.connect()
        await asyncio.sleep(50)
        await client.connect()


if __name__ == "__main__":
    asyncio.run(main())
