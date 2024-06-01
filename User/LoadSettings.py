import os
from dotenv import load_dotenv


class LoadUserSettingData:
    @ staticmethod
    def load_user_settings():
        load_dotenv('.env')
        flag = os.getenv(str("FLAG"))
        timeframes_string = os.getenv(str("TIMEFRAMES"))
        timeframes_list = timeframes_string.split(',')
        timeframes = tuple(timeframes_list)
        instIds_string = os.getenv(str("INSTIDS"))
        instIds_list = instIds_string.split(',')
        instIds = tuple(instIds_list)
        passphrase = os.getenv(str("PASSPHRASE"))
        api_key = os.getenv(str("API_KEY"))
        secret_key = os.getenv(str("SECRET_KEY"))
        return(flag, timeframes, instIds, passphrase, api_key, secret_key)
