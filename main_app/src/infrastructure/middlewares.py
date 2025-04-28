import contextlib
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import UUID

from main_app.src.application.interfaces import ISessionMiddleware
from main_app.src.infrastructure.repositories.sessions import (
    RedisSessionBackend, 
    GuestSessionBackend
)
from main_app.src.infrastructure.types import (
    RequestResponseEndpoint
)


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for managing authentication and guest sessions."""

    def __init__(
        self, 
        app: FastAPI, 
        redis_manager: RedisSessionBackend, 
        guest_manager: GuestSessionBackend
    ) -> None:
        """Initializes the session middleware with Redis and guest session backends.
        Args:
            app (FastAPI): The FastAPI application instance.
            redis_manager (RedisSessionBackend): Redis backend for managing authenticated sessions.
            guest_manager (GuestSessionBackend): Guest session manager for handling unauthenticated users.
        """
        super().__init__(app)
        self.redis_backend = redis_manager
        self.guest_manager = guest_manager

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Handles session retrieval, management, and cleanup for incoming requests.
        Execution Flow:
        - Extracts session ID from cookies (`auth_session` or `guest_session`).
        - If an authenticated session exists in Redis, it is loaded.
        - If no session is found, a new guest session is created.
        - Cleans up guest session data if an authenticated session is found.
        - Passes the request forward to the next middleware or handler.
        Args:
            request (Request): The incoming HTTP request.
            call_next (RequestResponseEndpoint): The next request handler in the middleware chain.
        Returns:
            Response: The processed HTTP response.
        """
        session_id = request.cookies.get("auth_session") or request.cookies.get("guest_session")
        request.state.session = None
        session_data = None  # ✅ Ensure session_data is always defined
        if session_id:
            with contextlib.suppress(ValueError):  # Prevents invalid UUID errors
                session_uuid = UUID(session_id)
                session_data = await self.redis_backend.read(session_uuid)
                request.state.session = session_data or session_id  # Properly assign session data
        if not request.state.session:
            # Either retrieve an existing guest session or create a new one
            guest_session = self.guest_manager.get_guest_session(request) or self.guest_manager.create_guest_session(Response())
            request.state.session = guest_session
        response: Response = await call_next(request)
        # Ensure session_data exists before cleanup
        if session_data:
            self.guest_manager.delete_guest_session(response)
        return response
