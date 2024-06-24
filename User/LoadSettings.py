import os, time, hmac, base64, hashlib, logging
from dotenv import load_dotenv

class LoadUserSettingData:
    def __init__(self):
        load_dotenv('.env')
        self.flag = str(os.getenv("FLAG"))
        self.timeframes = tuple(str(os.getenv("TIMEFRAMES")).split(','))
        self.instIds = tuple(str(os.getenv("INSTIDS")).split(','))
        self.passphrase = str(os.getenv("PASSPHRASE"))
        self.api_key = str(os.getenv("API_KEY"))
        self.secret_key = str(os.getenv("SECRET_KEY"))




    #Создание подписи для private подписки
    def create_signature(self):
        timestamp = int(time.time())
        sign = f'{timestamp}GET/users/self/verify'
        total_params = bytes(sign, encoding='utf-8')
        signature = hmac.new(bytes(self.secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        signature = str(signature, 'utf-8')
        return signature


    @staticmethod
    def set_logging_settings():
        ws_logger = logging.getLogger('websocket')
        ws_logger.setLevel(logging.DEBUG)
        ws_file_handler = logging.FileHandler("test.log")
        ws_logger.addHandler(ws_file_handler)
        return ws_logger