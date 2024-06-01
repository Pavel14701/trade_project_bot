#!/usr/bin/env python3
import redis
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData

# Загрузка пользовательских настроек
flag, timeframes, instIds, passphrase, api_key, secret_key = LoadUserSettingData.load_user_settings()

# Настройка подключения к базе данных
engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")
Base = declarative_base()

# Создание классов и таблиц
data_all_datasets = DataAllDatasets(instIds, timeframes)
classes_dict = data_all_datasets.create_classes(Base)
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)

# Настройка Redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# Функция для публикации сообщения
def publish_message(channel, message):
    r.publish(channel, message)

# Асинхронная функция для отправки сообщений каждые 15 секунд
async def send_messages_periodically():
    while True:
        publish_message('my-channel', '415 база ответьте')
        print('сообщение отправлено')
        await asyncio.sleep(15)  # Ожидание 15 секунд

if __name__ == "__main__":
    # Запуск асинхронной функции
    asyncio.run(send_messages_periodically())


    
