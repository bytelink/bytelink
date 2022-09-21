from __future__ import annotations

import asyncio

from bytelink.config import Config
from bytelink.network.client import Client


async def main() -> None:
    client = await Client.create((Config.IP, Config.PORT), timeout=3)

    async with client:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
