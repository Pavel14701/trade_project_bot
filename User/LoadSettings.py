import os, time, hmac, base64, hashlib
from typing import Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

class LoadUserSettingData:
    @staticmethod
    def load_api_setings() -> dict:
        load_dotenv()
        return {
            'flag': str(os.getenv("FLAG")),
            'api_key': str(os.getenv("API_KEY")),
            'passphrase': str(os.getenv("PASSPHRASE")),
            'secret_key': str(os.getenv("SECRET_KEY")),
        }

    @staticmethod
    def load_user_settings() -> dict:
        load_dotenv()
        return {
            'timeframes': tuple(str(os.getenv("TIMEFRAMES")).split(',')),
            'instIds': tuple(str(os.getenv("INSTIDS")).split(',')),
            'leverage': int(os.getenv('LEVERAGE')),
            'risk': float(os.getenv('RISK')),
            'mgnMode': str(os.getenv('MGNMODE'))
        }    


    @staticmethod
    def load_retry_requests_configs():
        load_dotenv()
        value = os.getenv('REQUESTDELAY')
        value = float(value) if '.' in value else int(value)
        return {
            'max_retries': int(os.getenv('MAXRETRYREQUESTS')),
            'delay': value
        }


    @staticmethod
    def load_cache_settings() -> dict:
        load_dotenv()
        return {
            'host': str(os.getenv("HOST")),
            'port': int(os.getenv("PORT")),
            'db': str(os.getenv("DB")),
        }
    
    @staticmethod
    def load_avsl_configs() -> dict:
        load_dotenv()
        return {
            'lenghtsFast': int(os.getenv("AVSLLENGHTSFAST")),
            'lenghtsSlow': int(os.getenv("AVSLLENGHTSSLOW")),
            'lenT': int(os.getenv("AVSLLENT")),
            'standDiv': float(os.getenv("AVSLSTANDDIV")),
            'offset': int(os.getenv("AVSLOFFSET"))
        }


    @staticmethod
    def load_bollinger_bands_settings() -> dict:
        load_dotenv()
        return {
            'lenghts': int(os.getenv("BBLENGHTS")),
            'stdev': float(os.getenv("BBSTDEV"))
        }


    @staticmethod
    def load_alma_configs() -> dict:
        load_dotenv()
        return {
            'lenghtsVSlow': int(os.getenv("ALMALENGHTSVSLOW")),
            'lenghtsSlow': int(os.getenv("ALMALENGHTSSLOW")),
            'lenghtsMiddle': int(os.getenv("ALMALENGHTSSMIDDLE")),
            'lenghtsFast': int(os.getenv("ALMALENGHTSFAST")),
            'lenghtsVFast': int(os.getenv("ALMALENGHTSVFAST")),
            'lenghts': int(os.getenv("ALMALENGHTS"))
        }


    @staticmethod
    def load_rsi_clouds_configs() -> dict:
        load_dotenv()
        return {
            'rsi_period': int(os.getenv('RSILENGHTS')),
            'rsi_scalar': int(os.getenv('RSISCALAR')),
            'rsi_drift': int(os.getenv('RSIDRIFT')),
            'rsi_offset': int(os.getenv('RSIOFFSET')),
            'macd_fast': int(os.getenv('MACDFAST')),
            'macd_slow': int(os.getenv('MACDSLOW')),
            'macd_signal': int(os.getenv('MACDSIGNAL')),
            'macd_offset': int(os.getenv('MACDOFFSET')),
            'calc_data': str(os.getenv('CALCDATA')),
            'talib': bool(os.getenv('RSICLOUDSTALIBCONFIG'))
        }


    @staticmethod
    def load_stoch_rsi_configs() -> dict:
        load_dotenv()
        return {
            'stoch_rsi_timeperiod': int(os.getenv('STOCHRSITIMEPERIOD')),
            'stoch_rsi_fastk_period': int(os.getenv('STOCHRSIFASTKPERIOD')),
            'stoch_rsi_fastd_period': int(os.getenv('STOCHRSIFASTDPERIOD')),
            'stoch_rsi_fastd_matype': int(os.getenv('STOCHRSIFASTDMATYPE'))
        }


    @staticmethod
    def load_vpci_configs() -> dict:
        load_dotenv()
        return {
            'vpci_long': int(os.getenv('VPCILONGPERIOD')),
            'vpci_short': int(os.getenv('VPCISHORTPERIOD'))
        }


    @staticmethod
    def load_adx_configs() -> dict:
        load_dotenv()
        return {
            'adx_timeperiod': int(os.getenv("ADXTIMEPERIOD")),
            'adx_trigger': int(os.getenv('ADXTRIGGER'))
        }


    @staticmethod
    def load_kama_configs() -> dict:
        load_dotenv()
        return {
            'kama_lengths': int(os.getenv('KAMALENGHTS')),
            'kama_fast':  int(os.getenv('KAMAFAST')),
            'kama_slow': int(os.getenv('KAMASLOW')),
            'kama_drift': int(os.getenv('KAMADRIFT')),
            'kama_offset': int(os.getenv('KAMAOFFSET'))
        }


    @staticmethod
    def load_mesa_adaptive_ma_configs() -> dict:
        load_dotenv()
        return {
            'mesa_fastlimit': float(os.getenv('MESAFASTLIMIT')),
            'mesa_slowlimit': float(os.getenv('MESASLOWLIMIT')),
            'mesa_prenan': int(os.getenv('MESAPRENAN')),
            'mesa_talib': bool(os.getenv('MESATALIB')),
            'mesa_offset': int(os.getenv('MESAOFFSET'))
        }


    @staticmethod
    def load_zigzag_configs() -> dict:
        load_dotenv()
        value = os.getenv('ZIGZAGDEVIATION')
        value = float(value) if '.' in value else int(value)
        return {
            'zigzag_legs': int(os.getenv('ZIGZAGLEGS')),
            'zigzag_deviation': value,
            'zigzag_retrace': bool(os.getenv('ZIGZAGRETRACE')),
            'zigzag_last_extreme': bool(os.getenv('ZIGZAGLASTEXTREME')),
            'zigzag_offset': int(os.getenv('ZIGZAGOFFSET'))
        }


    @staticmethod
    def load_vwma_adx_configs():
        load_dotenv()
        return {
            'vwma_adx_vwma_lenghts': int(os.getenv('VWMAADXVWMALENGHTS')),
            'vwma_adx_adx_period': int(os.getenv('VWMAADXADXPERIOD')),
            'vwma_adx_adx_threshold': int(os.getenv('VWMAADXADXTHRESHOLD')),
            'vwma_adx_adx_smooth': int(os.getenv('VWMAADXADXSMOOTH')),
            'vwma_adx_di_period': int(os.getenv('VWMAADXDIPERIOD'))
        }


    @staticmethod
    async def create_headers(
        sign:Optional[bool], request_path:Optional[str],
        body:Optional[str], method:Optional[str], flag:Optional[str]
        ) -> dict:
        if sign:
            settings = LoadUserSettingData.load_api_setings()
            timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat("T", "milliseconds") + 'Z'
            message = f'{timestamp}{method}{request_path}{body}'
            signature = base64.b64encode(hmac.new(settings['secret_key'].encode(), message.encode(), hashlib.sha256).digest()).decode()
            return {
                'OK-ACCESS-KEY': settings['api_key'],
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': settings['passphrase'],
                'x-simulated-trading': flag,
                'Content-Type': 'application/json'
            }
        else:
            return{
                'Content-Type': 'application/json',
                'x-simulated-trading': flag
            }


    @staticmethod
    async def create_signature_ws(secret_key:Optional[str]) -> dict:
        timestamp = int(time.time())
        sign = f'{timestamp}GET/users/self/verify'
        total_params = bytes(sign, encoding='utf-8')
        signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        signature = str(signature, 'utf-8')
        return {'timestamp': timestamp, 'signature': signature}