#!/usr/bin/env python3
from utils.IventListner import OKXIventListner
from User.LoadSettings import LoadUserSettingData


if __name__ == '__main__':
    settings = LoadUserSettingData.load_user_settings()
    listner_instance = OKXIventListner(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()
