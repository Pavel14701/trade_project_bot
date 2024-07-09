#!/usr/bin/env python3
import time
from threading import Thread
import schedule
from datasets.database import classes_dict, Session
from User.LoadSettings import LoadUserSettingData
from utils.StartDelayCalculator import StartDelayCalc
from User.Signals import AVSL_RSI_ClOUDS

# При инициализации нужно написать функцию, которая будет проверять есть ли стейт в SQL и вешать None,
# если соответствующий стейт не обнаружен и делать это она должна внутри !!!
settings = LoadUserSettingData.load_user_settings()
scriner_instance1 = AVSL_RSI_ClOUDS(Session, classes_dict, settings['instIds'][0], settings['timeframes'][0], 300)
scriner_instance2 = AVSL_RSI_ClOUDS(Session, classes_dict, settings['instIds'][0], settings['timeframes'][1], 300)
scriner_instance3 = AVSL_RSI_ClOUDS(Session, classes_dict, settings['instIds'][0], settings['timeframes'][2], 300)
scriner_instance4 = AVSL_RSI_ClOUDS(Session, classes_dict, settings['instIds'][0], settings['timeframes'][3], 300)


def check_signal1(scriner_instance1):
    state = scriner_instance1.check_active_state()
    if state is None:
        scriner_instance1.create_signals()
    elif state:
        scriner_instance1.trailing_stoploss()

def check_signal2(scriner_instance2):
    state = scriner_instance2.check_active_state()
    if state is None:
        scriner_instance2.create_signals()
    elif state:
        scriner_instance2.trailing_stoploss()


def check_signal3(scriner_instance3):
    state = scriner_instance3.check_active_state()
    if state is None:
        scriner_instance3.create_signals()
    elif state:
        scriner_instance3.trailing_stoploss()


def check_signal4(scriner_instance4):
    state = scriner_instance4.check_active_state()
    if state is None:
        scriner_instance4.create_signals()
    elif state:
        scriner_instance4.trailing_stoploss()


def run_job(job_func, arg):
    job_thread = Thread(target=job_func, args=(arg,))
    job_thread.start()


schedule.every(20).seconds.do(run_job, check_signal1, scriner_instance1)
schedule.every(40).seconds.do(run_job, check_signal2, scriner_instance2)
schedule.every(60).seconds.do(run_job, check_signal3, scriner_instance3)
schedule.every(80).seconds.do(run_job, check_signal4, scriner_instance4)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    #StartDelayCalc.startdelay()
    thread = Thread(target=run_schedule)
    thread.start()
