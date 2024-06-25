import os, time, hmac, base64, hashlib, logging
from dotenv import load_dotenv

class LoadUserSettingData:
    def __init__(self):
        load_dotenv()
        self.flag = str(os.getenv("FLAG"))
        self.timeframes = tuple(str(os.getenv("TIMEFRAMES")).split(','))
        self.instIds = tuple(str(os.getenv("INSTIDS")).split(','))
        self.passphrase = str(os.getenv("PASSPHRASE"))
        self.api_key = str(os.getenv("API_KEY"))
        self.secret_key = str(os.getenv("SECRET_KEY"))
        self.host = str(os.getenv("HOST"))
        self.port = int(os.getenv("PORT"))
        self.db = str(os.getenv("DB"))
        self.avsl_configs = {
            'lenghtsFast': int(os.getenv("AVSLlenghtsFast")),
            'lenghtsSlow': int(os.getenv("AVSLlenghtsSlow")),
            'lenT': int(os.getenv("AVSLlenT")),
            'standDiv': float(os.getenv("AVSLstandDiv")),
            'offset': int(os.getenv("AVSLoffset"))
        }
        self.bollinger_bands_settings = {
            'lenghts': int(os.getenv("BBlenghts")),
            'stdev': float(os.getenv("BBstdev"))
        }
        self.alma_configs = {
            'lenghtsVSlow': int(os.getenv("ALMAlenghtsVSlow")),
            'lenghtsSlow': int(os.getenv("ALMAlenghtsSlow")),
            'lenghtsMiddle': int(os.getenv("ALMAlenghtsMiddle")),
            'lenghtsFast': int(os.getenv("ALMAlenghtsFast")),
            'lenghtsVFast': int(os.getenv("ALMAlenghtsVFast")),
            'lenghts': int(os.getenv("ALMAlenghts"))
        }




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