import contextlib
from uuid import UUID

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from main_app.src.infrastructure.repositories.sessions import (
    GuestSessionBackend,
    RedisSessionBackend,
)
from main_app.src.infrastructure._types import RequestResponseEndpoint


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for managing authentication and guest sessions."""

    def __init__(
        self, 
        app: FastAPI, 
        redis_manager: RedisSessionBackend, 
        guest_manager: GuestSessionBackend
    ) -> None:
        """
        Initializes the session middleware with Redis and guest session backends.
        Args:
            app (FastAPI): The FastAPI application instance.
            redis_manager (RedisSessionBackend): Redis backend for managing
              authenticated sessions.
            guest_manager (GuestSessionBackend): Guest session manager for
              handling unauthenticated users.
        """
        super().__init__(app)
        self.redis_backend = redis_manager
        self.guest_manager = guest_manager

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Handles session retrieval, management, and cleanup for 
        incoming requests.
        Execution Flow:
        - Extracts session ID from cookies (`auth_session` or `guest_session`).
        - If an authenticated session exists in Redis, it is loaded.
        - If no session is found, a new guest session is created.
        - Cleans up guest session data if an authenticated session is found.
        - Passes the request forward to the next middleware or handler.
        Args:
            request (Request): The incoming HTTP request.
            call_next (RequestResponseEndpoint): The next request 
            handler in the middleware chain.
        Returns:
            Response: The processed HTTP response.
        """
        session_id = request.cookies.get(
            "auth_session"
        ) or request.cookies.get(
            "guest_session"
        )
        request.state.session = None
        session_data = None
        if session_id:
            with contextlib.suppress(ValueError):
                session_uuid = UUID(session_id)
                session_data = await self.redis_backend.read(session_uuid)
                request.state.session = session_data or session_id
        response: Response = await call_next(request)
        if not request.state.session:
            guest_session = self.guest_manager.create_guest_session(response)
            request.state.session = guest_session
            response.set_cookie(
                key="guest_session", 
                value=str(guest_session), 
                httponly=True
            )
        if session_data:
            self.guest_manager.delete_guest_session(response)
        return response
