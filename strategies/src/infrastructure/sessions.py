import asyncio

import httpx


async def fetch():
    async with httpx.AsyncClient(http2=True) as client:
        response1 = await client.get(
            "https://www.example.com", 
            headers={
                "User-Agent": "Client1"
            }
        )
        response2 = await client.post(
            "https://www.example.com", 
            headers={
                "User-Agent": "Client2",
                "Authorization": "Bearer token123"
            }
        )
        response3 = await client.get(
            "https://www.example.com", 
            headers={
                "User-Agent": "Client3",
                "Accept": "application/json"
            }
        )

        print(response1.status_code, response1.headers)
        print(response2.status_code, response2.headers)
        print(response3.status_code, response3.headers)


asyncio.run(fetch())


async def client_factory():
    async with httpx.AsyncClient(http2=True) as client:
        try:
            yield client
        finally:
            await client.aclose()