from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
from main_app.src.infrastructure.database import get_db
from main_app.src.infrastructure.models import User, UserSecrets
import uuid


router = APIRouter()


class AppRouters:
    def __init__(
        self,
        password_hasher: PasswordHasher,
        cipher: Fernet
    ) -> None:
        self._password_hasher = password_hasher
        self._cipher = cipher

    @router.post("/users/")
    async def create_user(self, username: str, password: str, db: AsyncSession = Depends(get_db)):
        """Создание пользователя с автоматическим хешированием пароля."""
        user = User(app_config={"pepper": "secret_pepper"}, password_hasher=self._password_hasher)
        user.username = username
        user.password = password
        db.add(user)
        await db.commit()
        return {"id": user.id, "username": user.username}

    @router.get("/users/{user_id}")
    async def get_user(self, user_id: int, db: AsyncSession = Depends(get_db)):
        """Получение информации о пользователе (без расшифровки пароля)."""
        user = await db.get(User, user_id)
        return {"id": user.id, "username": user.username}

    @router.post("/secrets/")
    async def create_user_secrets(self, user_id: int, api_key: str, secret_key: str, passphrase: str, db: AsyncSession = Depends(get_db)):
        """Создание секретов пользователя с автоматическим шифрованием."""
        user_secrets = UserSecrets(self._cipher)
        user_secrets.user_id = user_id
        user_secrets.api_key = api_key
        user_secrets.secret_key = secret_key
        user_secrets.passphrase = passphrase
        db.add(user_secrets)
        await db.commit()
        return {"message": "Secrets stored securely"}

    @router.get("/secrets/{user_id}")
    async def get_user_secrets(self, user_id: int, db: AsyncSession = Depends(get_db)):
        """Получение расшифрованных API-ключей."""
        user_secrets = await db.get(UserSecrets, user_id)
        
        return {
            "api_key": user_secrets.api_key,
            "secret_key": user_secrets.secret_key,
            "passphrase": user_secrets.passphrase
        }


class AuthRoutes:
    def __init__(self, password_hasher: PasswordHasher) -> None:
        self._password_hasher = password_hasher

    @router.post("/auth/login/")
    async def login(self, request: Request, response: Response, username: str, password: str, db: AsyncSession = Depends(get_db)):
        """Аутентификация пользователя через сессии"""
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if not user or not user.verify_password(password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        request.session["user_id"] = user.id
        return {"message": "Logged in successfully"}

    @router.get("/auth/logout/")
    async def logout(self, request: Request, response: Response):
        """Выход из системы, удаление сессии"""
        request.session.clear()
        return {"message": "Logged out successfully"}

    @router.get("/auth/me/")
    async def get_current_user(self, request: Request, db: AsyncSession = Depends(get_db)):
        """Получение текущего пользователя по сессии"""
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = await db.get(User, user_id)
        return {"id": user.id, "username": user.username}
