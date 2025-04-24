import asyncio
from app.consumer import broker, restart_lost_connections

async def main():
    await broker.start()
    await restart_lost_connections()

if __name__ == "__main__":
    asyncio.run(main())
