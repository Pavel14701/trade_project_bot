from threading import Thread
from utils.IventListner import OKXIventListner
from User.LoadSettings import LoadUserSettingData


settings = LoadUserSettingData.load_user_settings()
listner_instance1 = OKXIventListner(settings['instId'][0])
listner_instance2 = OKXIventListner(settings['instId'][1])


def listner1(listner_instance1):
    listner_instance1.create_listner()
    
thread1 = Thread(target=listner1)


def listner2(listner_instance2):
    listner_instance2.create_listner()

thread2 = Thread(target=listner2)


if __name__ == '__main__':
    thread1.start()
    thread2.start()
