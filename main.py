#!/usr/bin/env python3
import json, time, hmac, base64, logging, hashlib, asyncio, threading
import datetime, websockets
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData

# Асинхронный движок для подключения к базе данных
engine = create_async_engine("sqlite+aiosqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")
Base = declarative_base()

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession)

# Асинхронное создание таблиц в базе данных
async def create_tables():
    data_all_datasets = DataAllDatasets(instIds, timeframes)
    classes_dict = data_all_datasets.create_classes(Base)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Загрузка пользовательских настроек
flag, timeframes, instIds, passphrase, api_key, secret_key = LoadUserSettingData.load_user_settings()

# Logger
ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("test.log")
ws_logger.addHandler(ws_file_handler)

# Генерация подписи для WebSocket
timestamp = int(time.time())
sign = str(timestamp) + 'GET' + '/users/self/verify'
total_params = bytes(sign, encoding='utf-8')
signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
signature = base64.b64encode(signature)
signature = str(signature, 'utf-8')

# Функция для подписки на канал Redis в отдельном потоке
def listen_to_redis_channel():
    r = Redis(host='127.0.0.1', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe('my-channel')
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            print(f"Получено сообщение: {message['data'].decode('utf-8')}")
        time.sleep(1)

# Запуск слушателя Redis в отдельном потоке
thread = threading.Thread(target=listen_to_redis_channel)
thread.start()

# Основная асинхронная функция
async def main():
    await create_tables()
    # Ваш код для работы с WebSocket
    msg = {
        "op": "login",
        "args": [
            {
                "apiKey": api_key,
                "passphrase": passphrase,
                "timestamp": timestamp,
                "sign": signature
            }
        ]
    }
    async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as websocket:
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        ws_logger.info(f'Connected {datetime.datetime.now().isoformat()} - Response: {response}')

        subs = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "account",
                    "extraParams": "{\"updateInterval\": \"0\"}"
                }
            ]
        }
        await websocket.send(json.dumps(subs))

        async for msg in websocket:
            msg = json.loads(msg)
            print(msg)

# Запуск основной асинхронной функции
if __name__ == '__main__':
    asyncio.run(main())
    print("hello")
