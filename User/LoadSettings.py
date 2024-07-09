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
        self.leverage = int(os.getenv('LEVERAGE'))
        self.risk = float(os.getenv('RISK'))
        self.mgnMode = str(os.getenv('MGNMODE')) # cross or isolated
        self.avsl_configs = {
            'lenghtsFast': int(os.getenv("AVSLLENGHTSFAST")),
            'lenghtsSlow': int(os.getenv("AVSLLENGHTSSLOW")),
            'lenT': int(os.getenv("AVSLLENT")),
            'standDiv': float(os.getenv("AVSLSTANDDIV")),
            'offset': int(os.getenv("AVSLOFFSET"))
        }
        self.bollinger_bands_settings = {
            'lenghts': int(os.getenv("BBLENGHTS")),
            'stdev': float(os.getenv("BBSTDEV"))
        }
        self.alma_configs = {
            'lenghtsVSlow': int(os.getenv("ALMALENGHTSVSLOW")),
            'lenghtsSlow': int(os.getenv("ALMALENGHTSSLOW")),
            'lenghtsMiddle': int(os.getenv("ALMALENGHTSSMIDDLE")),
            'lenghtsFast': int(os.getenv("ALMALENGHTSFAST")),
            'lenghtsVFast': int(os.getenv("ALMALENGHTSVFAST")),
            'lenghts': int(os.getenv("ALMALENGHTS"))
        }
        self.clouds_rsi_configs = {
            'rsi_period_short': int(os.getenv("RSISHORTLENGHTS")),
            'rsi_period_long': int(os.getenv("RSILONGLENGHTS")),
            'ema_period': int(os.getenv("RSIEMALENGHTS"))
        }
        self.stoch_rsi_configs = {
            'stoch_rsi_timeperiod': int(os.getenv('STOCHRSITIMEPERIOD')),
            'stoch_rsi_fastk_period': int(os.getenv('STOCHRSIFASTKPERIOD')),
            'stoch_rsi_fastd_period': int(os.getenv('STOCHRSIFASTDPERIOD')),
            'stoch_rsi_fastd_matype': int(os.getenv('STOCHRSIFASTDMATYPE'))
        }
        self.adx_timeperiod = int(os.getenv("ADXTIMEPERIOD"))
        self.adx_trigger = int(os.getenv('ADXTRIGGER'))

    @staticmethod
    def load_user_settings() -> list:
        load_dotenv()
        return {
            'timeframes': list(str(os.getenv("TIMEFRAMES")).split(',')),
            'instIds': list(str(os.getenv("INSTIDS")).split(','))}
    



    #Создание подписи для private подписки
    async def create_signature(self) -> str:
        print(self.secret_key)
        timestamp = int(time.time())
        sign = f'{timestamp}GET/users/self/verify'
        total_params = bytes(sign, encoding='utf-8')
        signature = hmac.new(bytes(self.secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        signature = str(signature, 'utf-8')
        return timestamp, signature