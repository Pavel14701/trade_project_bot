#!/usr/bin/env python3
import json, time, logging, asyncio, threading
import datetime, websockets
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
    data_all_datasets = DataAllDatasets(instIds, flag, timeframes)
    classes_dict = data_all_datasets.create_classes(Base)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Загрузка пользовательских настроек
flag, timeframes, instIds, passphrase, api_key, secret_key, host, db, port = LoadUserSettingData.load_user_settings()
signature = LoadUserSettingData.create_signature(secret_key)


# Logger
ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("test.log")
ws_logger.addHandler(ws_file_handler)


# Запуск слушателя Redis в отдельном потоке
thread = threading.Thread(target=LoadUserSettingData.listen_to_redis_channel, args=(host, port, db))
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
                "timestamp": int(time.time()),
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
