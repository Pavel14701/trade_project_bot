#!/usr/bin/env python3
import time
from threading import Thread
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import schedule
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData
from utils.StartDelayCalculator import StartDelayCalc
from User.Signals import CheckSignalData

# Загрузка пользовательских настроек
flag, timeframes, instIds, passphrase, api_key, secret_key, host, db, port = LoadUserSettingData.load_user_settings()

# Настройка подключения к базе данных
engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")
Base = declarative_base()

# Создание классов и таблиц
data_all_datasets = DataAllDatasets(instIds, flag, timeframes)
classes_dict = data_all_datasets.create_classes(Base)
TradeSignals = data_all_datasets.create_TradeUserData(Base)
Base.metadata.create_all(engine)
print(f'\n\n{classes_dict}\n\n')
# Создание сессии
Session = sessionmaker(bind=engine)

# Функции для проверки сигналов
def check_signal_15m():
    signal = CheckSignalData.avsl_signals(flag, instIds[1], timeframes[0],
                                          Base, Session, classes_dict,
                                          host, port, db, lenghts=300)
    # Обработка сигнала

def check_signal_1H():
    signal = CheckSignalData.avsl_signals(flag, instIds[1], timeframes[1],
                                          Base, Session, classes_dict,
                                          host, port, db, lenghts=300)
    # Обработка сигнала

def check_signal_4H():
    signal = CheckSignalData.avsl_signals(flag, instIds[1], timeframes[2],
                                          Base, Session, classes_dict,
                                          host, port, db, lenghts=300)
    # Обработка сигнала

def check_signal_1D():
    signal = CheckSignalData.avsl_signals(flag, instIds[1], timeframes[3],
                                          Base, Session, classes_dict, 
                                          host, port, db, lenghts=300)
    # Обработка сигнала

# Функция для запуска задачи в отдельном потоке
def run_job(job_func):
    print(f"Запуск функции: {job_func.__name__}")
    job_thread = Thread(target=job_func)
    job_thread.start()

# Планировщик
schedule.every(20).seconds.do(run_job, check_signal_15m)
schedule.every(40).seconds.do(run_job, check_signal_1H)
schedule.every(60).seconds.do(run_job, check_signal_4H)
schedule.every(80).seconds.do(run_job, check_signal_1D)

# Функция для запуска планировщика
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Точка входа в программу
if __name__ == "__main__":
    #StartDelayCalc.startdelay()
    thread = Thread(target=run_schedule)
    thread.start()
