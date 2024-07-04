from threading import Thread
from utils.IventListner import OKXIventListner
from User.LoadSettings import LoadUserSettingData


settings = LoadUserSettingData.load_user_settings()
listner_instance1 = OKXIventListner(settings['instId'][0])
listner_instance2 = OKXIventListner(settings['instId'][1])


def listner1(listner_instance1):
    listner_instance1.create_listner()

def listner2(listner_instance2):
    listner_instance2.create_listner()


if __name__ == '__main__':
    
