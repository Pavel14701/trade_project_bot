#!/usr/bin/env python3
import time
from threading import Thread
import schedule
from datasets.database import create_classes, Base, Session
from User.LoadSettings import LoadUserSettingData
from utils.StartDelayCalculator import StartDelayCalc
from User.Signals import CheckSignalData

# При инициализации нужно написать функцию, которая будет проверять есть ли стейт в SQL и вешать None, -++++
# если соответствующий стейт не обнаружен и делать это она должна внутри !!!
Session, classes_dict, TradeUserData = create_classes(Base)




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
