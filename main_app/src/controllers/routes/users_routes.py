from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from main_app.src.infrastructure.database import get_db
from main_app.src.infrastructure.models import User

router = APIRouter()

@router.post("/")
async def create_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    """Создание пользователя"""
    user = User(username=username, password=password)
    db.add(user)
    await db.commit()
    return {"id": user.id, "username": user.username}

@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получение информации о пользователе"""
    user = await db.get(User, user_id)
    return {"id": user.id, "username": user.username}
