import asyncio
import websockets
import json
import time
import hmac
import base64
import hashlib
from app.redis_storage import store_connection, get_connection

class OKXWebsocketsChannel:
    """Класс WebSocket для пользователя."""

    def __init__(self, user_id: int, instType: str, account: bool, positions: bool, liq_warning: bool, api_key: str, secret_key: str, passphrase: str) -> None:
        self.user_id = user_id
        self.instType = instType
        self.account = account
        self.positions = positions
        self.liq_warning = liq_warning
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.websocket = None
        self.subscriptions = self._load_subscriptions()
        store_connection(self.user_id, self.__dict__)  # Сохраняем параметры в Redis

    def _load_subscriptions(self) -> list:
        """Загружает подписки пользователя."""
        subscriptions = []
        if self.account:
            subscriptions.append({"channel": "account"})
        if self.positions:
            subscriptions.append({"channel": "positions", "instType": self.instType})
        if self.liq_warning:
            subscriptions.append({"channel": "liquidation-warning", "instType": self.instType})
        return subscriptions

    async def subscribe_to_updates(self) -> None:
        """Запускает WebSocket и автоматически восстанавливает соединение при разрыве"""
        while True:
            try:
                await self._connect_and_listen()
            except websockets.ConnectionClosed:
                print(f"[{self.user_id}] WebSocket отключён, попытка переподключения...")
                await asyncio.sleep(5)  # Ожидание перед восстановлением

    async def _connect_and_listen(self) -> None:
        """Открывает WebSocket и слушает сообщения"""
        async with websockets.connect("wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999") as self.websocket:
            await self._login()
            await self._subscribe_channels()
            while True:
                try:
                    message = await self.websocket.recv()
                    print(f"[{self.user_id}] Получено сообщение: {message}")
                except websockets.ConnectionClosed:
                    print(f"[{self.user_id}] Соединение разорвано. Переподключение...")
                    await self.subscribe_to_updates()  # Перезапуск WebSocket

    async def _login(self) -> None:
        """Авторизация через WebSocket"""
        timestamp = int(time.time())
        sign = f"{timestamp}GET/users/self/verify"
        signature = base64.b64encode(hmac.new(
            bytes(self.secret_key, encoding="utf-8"),
            bytes(sign, encoding="utf-8"),
            hashlib.sha256
        ).digest()).decode("utf-8")

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
        """Подписывается на доступные события"""
        if self.subscriptions:
            await self.websocket.send(json.dumps({"op": "subscribe", "args": self.subscriptions}))
