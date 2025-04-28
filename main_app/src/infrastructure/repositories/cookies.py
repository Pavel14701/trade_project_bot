from fastapi import Request, Response

from main_app.src.application.interfaces import ICookieBackend

class CookieRepo(ICookieBackend):
    """Class for managing cookies: guest and authenticated sessions."""
    
    _GUEST_COOKIE = "guest_session"
    _AUTH_COOKIE = "auth_session"
    _DATA_COOKIE = "guest_data"

    def set_cookie(self, response: Response, key: str, value: str, max_age: int = 86400) -> None:
        """Sets or updates a cookie."""
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            max_age=max_age,
            secure=True,
            samesite="strict"
        )

    def get_cookie(self, request: Request, key: str) -> str | None:
        """Retrieves the value of a cookie."""
        return request.cookies.get(key)

    def delete_cookie(self, response: Response, key: str) -> None:
        """Deletes a cookie by setting an empty value."""
        response.set_cookie(
            key=key,
            value="",
            max_age=0,
            httponly=True,
            secure=True,
            samesite="strict"
        )
