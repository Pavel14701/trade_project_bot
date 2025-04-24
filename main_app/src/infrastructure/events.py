from fastapi import FastAPI
import asyncio
from sqlalchemy.orm import Session
from models import User, WebSocketConfig
from app.infrastructure.models import SessionLocal
from websockets_handler import OKXWebsocketsChannel

app = FastAPI()
active_users = {}

@app.on_event("startup")
async def startup_event():
    db: Session = SessionLocal()
    users = db.query(User).all()

    for user in users:
        configs = db.query(WebSocketConfig).filter(WebSocketConfig.user_id == user.id).first()
        
        if configs:
            ws_channel = OKXWebsocketsChannel(
                user_id=user.id, instType=configs.instType, 
                account=configs.account, positions=configs.positions, 
                liq_warning=configs.liq_warning
            )
            active_users[user.id] = ws_channel
            asyncio.create_task(ws_channel.subscribe_to_updates())

    db.close()
