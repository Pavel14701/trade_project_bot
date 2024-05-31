#!/usr/bin/env python3
import os, json, time, asyncio, hmac, base64, logging, hashlib
import datetime, websockets, schedule, nest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData
 

# Асинхронный движок для подключения к базе данных
engine = create_async_engine("sqlite+aiosqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")

# Создаем базовый класс для декларативных классов
Base = declarative_base()

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession)

# Асинхронное создание таблиц в базе данных
async def create_tables():
    print(type(timeframes), type(instIds))
    data_all_datasets = DataAllDatasets(instIds, timeframes)
    classes_dict = data_all_datasets.create_classes(Base)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# load env
load_dotenv(".env")
flag, timeframes, instIds, passphrase, api_key, secret_key = LoadUserSettingData.load_user_settings()


# logger
ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("test.log")
ws_logger.addHandler(ws_file_handler)

timestamp = int(time.time())
sign = str(timestamp) + 'GET' + '/users/self/verify'
total_params = bytes(sign, encoding='utf-8')
signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
signature = base64.b64encode(signature)
signature = str(signature, 'utf-8')

print("signature = {0}".format(signature))

# Основная асинхронная функция
async def main():
    # Создаем таблицы, если они еще не существуют
    await create_tables()

    # Ваш код для работы с WebSocket и другие асинхронные операции
    msg = \
        {
            "op": "login",
            "args": [
                {
                    "apiKey": f'{api_key}',
                    "passphrase": f'{passphrase}',
                    "timestamp": f'{timestamp}',
                    "sign": f'{signature}'
                }
            ]
        }

    async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as websocket:
        print(msg)
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(response)
        ws_logger.info('Connected ' + datetime.datetime.now().isoformat())

        subs = dict(
            op='subscribe',
            args=[
                dict(
                    channel='account',
                    extraParams='{\"updateInterval\": \"0\"}'
                )]
        )
        await websocket.send(json.dumps(subs))

        async for msg in websocket:
            msg = json.loads(msg)
            print(msg)

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
