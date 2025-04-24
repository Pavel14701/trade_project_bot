import asyncio
import json
import time
import hmac
import base64
import hashlib
import websockets
from sqlalchemy.orm import Session
from app.infrastructure.models import SessionLocal
from app.infrastructure.models import WebSocketConfig

class OKXWebsocketsChannel:
    """Класс для управления WebSocket-подключением пользователя."""

    def __init__(self, user_id: int, db_session: Session) -> None:
        self.user_id = user_id
        self.websocket = None
        
        # Загружаем конфигурацию пользователя из базы данных
        user_config = db_session.query(WebSocketConfig).filter(WebSocketConfig.user_id == user_id).first()
        if not user_config:
            raise ValueError(f"Не найдены настройки WebSocket для пользователя {user_id}")

        self.instType = user_config.instType
        self.account = user_config.account
        self.positions = user_config.positions
        self.liq_warning = user_config.liq_warning

        # API-ключи хранятся отдельно для каждого пользователя
        self.api_key, self.secret_key, self.passphrase = self._get_api_credentials(user_id)

    def _get_api_credentials(self, user_id: int) -> tuple:
        """Получает API-ключи пользователя (предполагаем, что они хранятся в БД)."""
        db = SessionLocal()
        config = db.query(WebSocketConfig).filter(WebSocketConfig.user_id == user_id).first()
        db.close()
        return config.api_key, config.secret_key, config.passphrase

    async def subscribe_to_updates(self) -> None:
        """Запускает подписку на обновления."""
        await self._create_signature_ws()
        async with websockets.connect("wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999") as self.websocket:
            await self._login()
            await self._subscribe_channels()
            await self._catch_messages()

    async def _create_signature_ws(self) -> tuple[int, str]:
        """Создаёт подпись для авторизации."""
        timestamp = int(time.time())
        sign = f"{timestamp}GET/users/self/verify"
        signature = base64.b64encode(hmac.new(
            bytes(self.secret_key, encoding="utf-8"),
            bytes(sign, encoding="utf-8"),
            hashlib.sha256
        ).digest()).decode("utf-8")
        return timestamp, signature

    async def _login(self, timestamp: int, signature: str) -> None:
        """Авторизация через WebSocket."""
        msg = {
            "op": "login",
            "args": [{
                "apiKey": self.api_key,
                "passphrase": self.passphrase,
                "timestamp": timestamp,
                "sign": signature,
            }]
        }
        await self.websocket.send(json.dumps(msg))
        response = await self.websocket.recv()
        print(f"[{self.user_id}] Авторизация: {response}")

    async def _subscribe_channels(self) -> None:
        """Подписывается на выбранные каналы."""
        subscriptions = []
        if self.account:
            subscriptions.append({"channel": "account"})
        if self.positions:
            subscriptions.append({"channel": "positions", "instType": self.instType})
        if self.liq_warning:
            subscriptions.append({"channel": "liquidation-warning", "instType": self.instType})
        if subscriptions:
            await self.websocket.send(json.dumps({"op": "subscribe", "args": subscriptions}))

    async def _catch_messages(self) -> None:
        """Бесконечно слушает WebSocket-соединение."""
        while True:
            try:
                response = await self.websocket.recv()
                print(f"[{self.user_id}] Получено сообщение: {response}")
            except websockets.ConnectionClosed:
                print(f"[{self.user_id}] Соединение закрыто, перезапуск...")
                await asyncio.sleep(5)
                await self.subscribe_to_updates()
