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
        """Initializes the session middleware with Redis and guest session backends."""
        super().__init__(app)
        self.redis_backend = redis_manager
        self.guest_manager = guest_manager

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Middleware execution logic:
        - Retrieves the session ID from cookies (`auth_session` or `guest_session`).
        - If an authenticated session exists in Redis, it is loaded.
        - If no session is found, a new guest session is created.
        - Deletes guest session data if an authenticated session is found.
        - Passes the request forward to the next middleware/handler.
        """
        session_id = request.cookies.get("auth_session") or request.cookies.get("guest_session")
        request.state.session = None
        if session_id:
            with contextlib.suppress(ValueError):  # Prevents invalid UUID errors
                session_uuid = UUID(session_id)
                session_data = await self.redis_backend.read(session_uuid)
                request.state.session = session_data or session_id
        if not request.state.session:
            # Either retrieve an existing guest session or create a new one
            guest_session = self.guest_manager.get_guest_session(request) or self.guest_manager.create_guest_session(Response())
            request.state.session = guest_session
        response: Response = await call_next(request)
        # Cleanup: If an authenticated session exists, remove any guest session data
        if session_data:
            self.guest_manager.delete_guest_session(response)
        return response
