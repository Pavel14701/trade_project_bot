from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
from main_app.src.infrastructure.database import get_db
from main_app.src.infrastructure.models import UserSecrets

router = APIRouter()

class SecretsRoutes:
    def __init__(self, cipher: Fernet) -> None:
        self._cipher = cipher

    @router.post("/")
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

    @router.get("/{user_id}")
    async def get_user_secrets(self, user_id: int, db: AsyncSession = Depends(get_db)):
        """Получение расшифрованных API-ключей."""
        user_secrets = await db.get(UserSecrets, user_id)
        return {
            "api_key": user_secrets.api_key,
            "secret_key": user_secrets.secret_key,
            "passphrase": user_secrets.passphrase
        }
