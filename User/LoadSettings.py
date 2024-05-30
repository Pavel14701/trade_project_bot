import os

class LoadUserSettingData:

    @ staticmethod
    def load_user_settings():
        flag = os.getenv("FLAG")
        timeframes_string = os.getenv("TIMEFRAMES")
        timeframes_list = timeframes_string.split(',')
        timeframes = tuple(timeframes_list)
        instIds_string = os.getenv("INSTIDS")
        instIds_list = instIds_string.split(',')
        instIds = tuple(instIds_list)
        passphrase = os.getenv("PASSPHRASE")
        api_key = os.getenv("API_KEY")
        secret_key = os.getenv("SECRET_KEY")
        return(flag, timeframes, instIds, passphrase, api_key, secret_key)
