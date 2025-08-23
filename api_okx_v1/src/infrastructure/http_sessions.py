import asyncio
from typing import (
    Any, 
    AsyncGenerator, 
    NoReturn
)


from api_okx_v1.src.infrastructure._types import (
    MarketClient, 
    PrivateClient,
)


class RateLimiter:
    """
    Asynchronous rate limiter that restricts the number of operations 
    (e.g., HTTP requests) to a specified maximum within a given time interval.

    This class uses an asyncio.Semaphore to control access and a background 
    task to periodically reset the available "tokens" for operations. It is 
    useful for enforcing API rate limits or throttling concurrent tasks.

    Attributes:
        rate (int): Maximum number of allowed operations per interval.
        interval (float): Time window in seconds during which the rate applies.
        _semaphore (asyncio.Semaphore): Internal semaphore tracking available operations.
        _reset_task (asyncio.Task): Background task that replenishes the semaphore periodically.
    """

    def __init__(self, rate: int, interval: float = 1.0) -> None:
        """
        Initializes the RateLimiter with a given rate and interval.

        Args:
            rate (int): Maximum number of allowed operations per interval.
            interval (float, optional): Duration of the interval in seconds. Defaults to 1.0.
        """
        self.rate = rate
        self.interval = interval
        self._semaphore = asyncio.Semaphore(rate)
        self._reset_task = asyncio.create_task(self._reset_loop())

    async def _reset_loop(self) -> NoReturn:
        """
        Internal coroutine that runs in the background and resets the semaphore 
        every `interval` seconds to allow new operations.

        This loop calculates how many tokens are missing from the semaphore 
        (i.e., how many operations were performed) and releases that many tokens 
        to restore the full quota.

        Note:
            This method runs indefinitely until `close()` is called.
        """
        while True:
            await asyncio.sleep(self.interval)
            for _ in range(self.rate - self._semaphore._value):
                self._semaphore.release()

    async def acquire(self) -> None:
        """
        Acquires permission to perform an operation.

        If the rate limit has been reached, this coroutine will block until 
        a token becomes available (i.e., until the next interval reset).
        """
        await self._semaphore.acquire()

    async def close(self) -> None:
        """
        Gracefully shuts down the rate limiter by cancelling the background 
        reset loop.

        This should be called when the rate limiter is no longer needed, 
        such as during application shutdown or cleanup.
        """
        self._reset_task.cancel()


class MarketClientPool:
    """
    A pool manager for MarketClient instances with built-in rate limiting.

    This class maintains a fixed-size pool of reusable MarketClient connections,
    allowing concurrent access while enforcing a global rate limit. Clients are
    acquired from an internal queue and returned automatically after use.

    Attributes:
        pool_size (int): Number of MarketClient instances to maintain in the pool.
        rate_limit (int): Maximum number of client acquisitions allowed per second.
        _queue (asyncio.Queue): Internal queue holding available MarketClient instances.
        _clients (list[MarketClient]): List of all initialized MarketClient instances.
        _limiter (RateLimiter): Rate limiter controlling access frequency.
        _initialized (bool): Flag indicating whether the pool has been initialized.
    """

    def __init__(self, pool_size: int = 5, rate_limit: int = 20):
        """
        Initialize the MarketClientPool with the specified pool size and rate limit.

        Args:
            pool_size (int): Number of clients to create and manage in the pool.
            rate_limit (int): Maximum number of client acquisitions per second.
        """
        self._pool_size = pool_size
        self._rate_limit = rate_limit
        self._queue: asyncio.Queue[MarketClient] = asyncio.Queue()
        self._clients: list[MarketClient] = []
        self._limiter = RateLimiter(rate_limit)
        self._initialized = False

    async def init(self) -> None:
        """
        Asynchronously initialize the pool by creating and entering each MarketClient.

        This method must be called before using the pool. It ensures that all clients
        are properly initialized and placed into the queue for use.

        Raises:
            RuntimeError: If called more than once without resetting the pool.
        """
        if self._initialized:
            return
        for _ in range(self._pool_size):
            client = MarketClient(http2=True)
            await client.__aenter__()
            self._clients.append(client)
            await self._queue.put(client)
        self._initialized = True

    async def get(self) -> AsyncGenerator[MarketClient, None]:
        """
        Acquire a MarketClient from the pool with rate limiting.

        This method yields a client for use and ensures it is returned to the pool
        after the calling context completes. Rate limiting is enforced before acquisition.

        Yields:
            MarketClient: A reusable client instance from the pool.

        Example:
            async for client in pool.get():
                response = await client.get(...)
        """
        await self._limiter.acquire()
        client = await self._queue.get()
        try:
            yield client
        finally:
            await self._queue.put(client)

    async def aclose(self) -> None:
        """
        Gracefully close all clients and release resources.

        This method should be called when the application shuts down or the pool
        is no longer needed. It closes the rate limiter and all managed clients.
        """
        await self._limiter.close()
        for client in self._clients:
            await client.aclose()


async def client_factory() -> AsyncGenerator[PrivateClient, Any]:
    """
    Asynchronous factory function that yields an HTTPX AsyncClient instance.

    This function creates an `httpx.AsyncClient` configured to support HTTP/2, 
    and yields it for use in asynchronous operations such as making HTTP requests. 
    Once the client is no longer needed, it ensures proper cleanup by closing the 
    connection gracefully.

    Yields:
        httpx.AsyncClient: An instance of HTTPX's asynchronous client.

    """
    async with PrivateClient(http2=True) as client:
        try:
            yield client
        finally:
            await client.aclose()