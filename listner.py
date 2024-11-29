#!/usr/bin/env python3
import asyncio
from websockets_sub.okx_websockets_channel import OKXWebsocketsChannel
from datasets.tables import create_tables_async


async def main():
    await create_tables_async()
    await OKXWebsocketsChannel('ANY', True, True, True).subscribe_to_updates()


if __name__ == '__main__':
    asyncio.run(main())