from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from argon2 import PasswordHasher
from main_app.src.infrastructure.database import get_db
from main_app.src.infrastructure.models import User

router = APIRouter()

class AuthRoutes:
    def __init__(self, password_hasher: PasswordHasher) -> None:
        self._password_hasher = password_hasher

    @router.post("/login/")
    async def login(self, request: Request, response: Response, username: str, password: str, db: AsyncSession = Depends(get_db)):
        """Аутентификация пользователя через сессии"""
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user or not user.verify_password(password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        request.session["user_id"] = user.id
        return {"message": "Logged in successfully"}

    @router.get("/logout/")
    async def logout(self, request: Request, response: Response):
        """Выход из системы, удаление сессии"""
        request.session.clear()
        return {"message": "Logged out successfully"}

    @router.get("/me/")
    async def get_current_user(self, request: Request, db: AsyncSession = Depends(get_db)):
        """Получение текущего пользователя по сессии"""
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = await db.get(User, user_id)
        return {"id": user.id, "username": user.username}
