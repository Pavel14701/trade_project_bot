import base64
import hashlib
import hmac
import json
import time
from typing import Dict

import websockets
from faststream.rabbit import RabbitBroker
from websockets import ClientConnection

from account_events.src.domain.entities import WebSocketDM


class OKXWebsocketsChannelGateway:
    def __init__(self, broker: RabbitBroker) -> None:
        """ 
        Инициализация WebSocket с возможностью работы
        сразу с несколькими пользователями.
        """
        self._broker: RabbitBroker = broker
        self.websocket_sessions: Dict[int, ClientConnection] = {}

    async def connect(self, config: WebSocketDM) -> None:
        """
        Открывает WebSocket-соединение для конкретного пользователя
        и управляет всеми активными подключениями.
        """
        if config.user_id in self.websocket_sessions:
            await self.close_connection(config.user_id)
        async with websockets.connect(
            "wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"
        ) as websocket:
            self.websocket_sessions[config.user_id] = websocket
            await self.login_user(config)
            await self.subscribe(config)
            while True:
                message = await websocket.recv(decode=True)
                await self.message_handler(config.user_id, message)

    async def login_user(self, config: WebSocketDM) -> None:
        """Авторизует пользователя в WebSocket."""
        websocket = self.websocket_sessions.get(config.user_id)
        if not websocket:
            return
        timestamp: int = int(time.time())
        await websocket.send(json.dumps({
            "op": "login",
            "args": [{
                "apiKey": config.api_key,
                "passphrase": config.passphrase,
                "timestamp": timestamp,
                "sign": self.generate_signature(config, timestamp),
            }]
        }))

    async def subscribe(self, config: WebSocketDM) -> None:
        """Осуществляет подписку на события для конкретного пользователя."""
        websocket = self.websocket_sessions.get(config.user_id)
        if not websocket:
            return
        subscriptions: list[dict] = [
            {"channel": event, "instType": config.instType}
            if event in ["positions", "liquidation-warning"]
            else {"channel": event}
            for event in ["account", "positions", "liquidation-warning"]
            if getattr(config, event)
        ]
        if subscriptions:
            await websocket.send(
                json.dumps({"op": "subscribe", "args": subscriptions})
            )

    async def close_connection(self, user_id: int) -> None:
        """Закрывает WebSocket-соединение пользователя, если оно активно."""
        websocket = self.websocket_sessions.pop(user_id, None)
        if websocket and websocket.close_code is None:
            await websocket.close()

    async def update_subscriptions(self, config: WebSocketDM) -> None:
        """Закрывает старое соединение перед обновлением подписок и запускает новое."""
        await self.close_connection(config.user_id)
        await self.connect(config)

    async def message_handler(self, user_id: int, message: str) -> None:
        """Отправляет сообщение в очередь RabbitMQ."""
        await self._broker.publish(
            message={"user_id": user_id, "message": message},
            queue="account_events"
        )

    def generate_signature(self, config: WebSocketDM, timestamp: int) -> str:
        """Создаёт подпись для авторизации конкретного пользователя."""
        return base64.b64encode(hmac.new(
            bytes(config.secret_key, encoding="utf-8"),
            bytes(f"{timestamp}GET/users/self/verify", encoding="utf-8"),
            hashlib.sha256
        ).digest()).decode("utf-8")
