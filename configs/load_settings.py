import os
from dotenv import load_dotenv


class ConfigsProvider:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_setings()
        return cls._instance


    def load_setings(self) -> None:
        load_dotenv()
        value_logging = os.getenv('REQUESTDELAY')
        value_adx = int(os.getenv('ADXADXRLENGHTS'))
        value_zigzag = os.getenv('ZIGZAGDEVIATION')
        value_zigzag = float(value_zigzag) if '.' in value_zigzag else int(value_zigzag)
        self.settings = {
            'api': {
                'flag': str(os.getenv("FLAG")),
                'api_key': str(os.getenv("API_KEY")),
                'passphrase': str(os.getenv("PASSPHRASE")),
                'secret_key': str(os.getenv("SECRET_KEY")),
            },
            'cache': {
                'host': str(os.getenv('REDISHOST')),
                'port': int(os.getenv('REDISPORT')),
                'db': int(os.getenv('REDISDB'))
            },
            'debug_logging_configs': {
                'max_retries': int(os.getenv('MAXRETRYREQUESTS')),
                'delay': float(value_logging) if '.' in value_logging else int(value_logging),
                'write_logs': bool(os.getenv('WRITELOGS')),
                'debug': bool(os.getenv('DEBUG'))
            },
            'user_settings': {
                'timeframes': tuple(str(os.getenv("TIMEFRAMES")).split(',')),
                'instIds': tuple(str(os.getenv("INSTIDS")).split(',')),
                'leverage': int(os.getenv('LEVERAGE')),
                'risk': float(os.getenv('RISK')),
                'mgnMode': str(os.getenv('MGNMODE'))
            },
            'indicators': {
                'avsl_configs': {
                    'lenghtsFast': int(os.getenv("AVSLLENGHTSFAST")),
                    'lenghtsSlow': int(os.getenv("AVSLLENGHTSSLOW")),
                    'lenT': int(os.getenv("AVSLLENT")),
                    'standDiv': float(os.getenv("AVSLSTANDDIV")),
                    'offset': int(os.getenv("AVSLOFFSET"))
                },
                'bollinger_bands_settings': {
                    'lenghts': int(os.getenv("BBLENGHTS")),
                    'stdev': float(os.getenv("BBSTDEV")),
                    'bb_ddof': int(os.getenv('BBDDOF')),
                    'bb_mamode': str(os.getenv('BBMAMODE')),
                    'bb_talib': bool(os.getenv('BBTALIB')),
                    'bb_offset': int(os.getenv('BBOFFSET'))
                },
                'alma_configs': {
                    'lenghtsVSlow': int(os.getenv("ALMALENGHTSVSLOW")),
                    'lenghtsSlow': int(os.getenv("ALMALENGHTSSLOW")),
                    'lenghtsMiddle': int(os.getenv("ALMALENGHTSSMIDDLE")),
                    'lenghtsFast': int(os.getenv("ALMALENGHTSFAST")),
                    'lenghtsVFast': int(os.getenv("ALMALENGHTSVFAST")),
                    'lenghts': int(os.getenv("ALMALENGHTS"))
                },
                'rsi_clouds_configs': {
                    'rsi_period': int(os.getenv('RSICLOUDSRSILENGHTS')),
                    'rsi_scalar': int(os.getenv('RSICLOUDSRSISCALAR')),
                    'rsi_drift': int(os.getenv('RSICLOUDSRSIDRIFT')),
                    'rsi_offset': int(os.getenv('RSICLOUDSRSIOFFSET')),
                    'rsi_mamode': str(os.getenv('RSICLOUDSMAMODE')),
                    'rsi_talib_config': bool(os.getenv('RSICLOUDSRSITALIBCONFIG')),
                    'macd_fast': int(os.getenv('RSICLOUDSMACDFAST')),
                    'macd_slow': int(os.getenv('RSICLOUDSMACDSLOW')),
                    'macd_signal': int(os.getenv('RSICLOUDSMACDSIGNAL')),
                    'macd_offset': int(os.getenv('RSICLOUDSMACDOFFSET')),
                    'calc_data': str(os.getenv('RSICLOUDSCALCDATA')),
                    'macd_talib_config': bool(os.getenv('RSICLOUDSMACDTALIBCONFIG'))
                },
                'stoch_rsi_configs': {
                    'stoch_rsi_timeperiod': int(os.getenv('STOCHRSITIMEPERIOD')),
                    'stoch_rsi_fastk_period': int(os.getenv('STOCHRSIFASTKPERIOD')),
                    'stoch_rsi_fastd_period': int(os.getenv('STOCHRSIFASTDPERIOD')),
                    'stoch_rsi_fastd_matype': int(os.getenv('STOCHRSIFASTDMATYPE'))
                },
                'vpci_configs': {
                    'vpci_long': int(os.getenv('VPCILONGPERIOD')),
                    'vpci_short': int(os.getenv('VPCISHORTPERIOD'))
                },
                'adx_configs': {
                    'adx_timeperiod': int(os.getenv('ADXTIMEPERIOD')),
                    'adx_lenghts_sig': int(os.getenv('ADXLENGHTSSIG')),
                    'adx_adxr_lenghts': None if value_adx ==0 else value_adx,
                    'adx_scalar': int(os.getenv('ADXSCALAR')),
                    'adx_talib': bool(os.getenv('ADXTALIB')),
                    'adx_tvmode': bool(os.getenv('ADXTVMODE')),
                    'adx_mamode': str(os.getenv('ADXMAMODE')),
                    'adx_drift': int(os.getenv('ADXDRIFT')),
                    'adx_offset': int(os.getenv('ADXOFFSET')),
                    'adx_trigger': int(os.getenv('ADXTRIGGER'))
                },
                'kama_configs': {
                    'kama_lengths': int(os.getenv('KAMALENGHTS')),
                    'kama_fast':  int(os.getenv('KAMAFAST')),
                    'kama_slow': int(os.getenv('KAMASLOW')),
                    'kama_drift': int(os.getenv('KAMADRIFT')),
                    'kama_offset': int(os.getenv('KAMAOFFSET'))
                },
                'mesa_adaptive_ma_configs': {
                    'mesa_fastlimit': float(os.getenv('MESAFASTLIMIT')),
                    'mesa_slowlimit': float(os.getenv('MESASLOWLIMIT')),
                    'mesa_prenan': int(os.getenv('MESAPRENAN')),
                    'mesa_talib': bool(os.getenv('MESATALIB')),
                    'mesa_offset': int(os.getenv('MESAOFFSET'))
                },
                'zigzag_configs': {
                    'zigzag_legs': int(os.getenv('ZIGZAGLEGS')),
                    'zigzag_deviation': value_zigzag,
                    'zigzag_retrace': bool(os.getenv('ZIGZAGRETRACE')),
                    'zigzag_last_extreme': bool(os.getenv('ZIGZAGLASTEXTREME')),
                    'zigzag_offset': int(os.getenv('ZIGZAGOFFSET'))
                },
                'vwma_adx_configs': {
                    'vwma_adx_vwma_lenghts': int(os.getenv('VWMAADXVWMALENGHTS')),
                    'vwma_adx_adx_period': int(os.getenv('VWMAADXADXPERIOD')),
                    'vwma_adx_adx_threshold': int(os.getenv('VWMAADXADXTHRESHOLD')),
                    'vwma_adx_adx_smooth': int(os.getenv('VWMAADXADXSMOOTH')),
                    'vwma_adx_di_period': int(os.getenv('VWMAADXDIPERIOD'))
                },
                'crsi_configs': {
                    'crsi_domcycle': int(os.getenv('CRSIDOMCYCLE')),
                    'crsi_vibration': int(os.getenv('CRSIVIBRATION')),
                    'crsi_leveling': float(os.getenv('CRSILEVELING'))
                },
                'bayes_ultimate_osc_configs':{
                    'bb_sma_period': int(os.getenv('BUOBBSMA')),
                    'bb_stddev_mult': float(os.getenv('BUOBBSTDDEVMULT')),
                    'ao_fast': int(os.getenv('BUOAOFAST')),
                    'ao_slow': int(os.getenv('BUOAOSLOW')),
                    'ac_fast': int(os.getenv('BUOACFAST')),
                    'ac_slow': int(os.getenv('BUOACSLOW')),
                    'ma_ac_ao_period': int(os.getenv('BUOMAACAOPERIOD')),
                    'lips_length': int(os.getenv('BUOLIPSLENGTH')),
                    'teeth_length': int(os.getenv('BUOTEETHLENGTH')),
                    'jaw_length': int(os.getenv('BUOJAWLENGTH')),
                    'lips_offset': int(os.getenv('BUOLIPSOFFSET')),
                    'teeth_offset': int(os.getenv('BUOTEETHOFFSET')),
                    'jaw_offset': int(os.getenv('BUOJAWOFFSET')),
                    'rsi_length': int(os.getenv('BUORSILENGTH')),
                    'macd_fast': int(os.getenv('BUOMACDFAST')),
                    'macd_slow': int(os.getenv('BUOMACDSLOW')),
                    'macd_signal': int(os.getenv('BUOMACDSIGNAL')),
                    'adx_length': int(os.getenv('BUOADXLENGTH')),
                    'adx_triger': int(os.getenv('BUOADXTRIGGER')),
                    'mesa_fastlimit': float(os.getenv('BUOMESAFASTLIMIT')),
                    'mesa_slowlimit': float(os.getenv('BUOMESASLOWLIMIT')),
                    'aroon_length': int(os.getenv('BUOAROONLENGHTS')),
                    'bayes_period': int(os.getenv('BUOBAYESPERIOD')),
                    'lower_threshold': float(os.getenv('BUOLOWERTHRESHOLD')),
                    'use_bw_confirmation': bool(os.getenv('BUOUSEBWCONF')),
                    'rsi_divergences': bool(os.getenv('BUOUSERSIDIVERS')),
                }
            }
        }


    def load_api_configs(self) -> dict:
        return self.settings['api']


    def load_cache_configs(self) -> dict:
        return self.settings['cache']
        

    def load_debug_logging_configs(self) -> dict:
        return self.settings['debug_logging_configs']


    def load_user_configs(self) -> dict:
        return self.settings['user_settings']


    def load_avsl_configs(self) -> dict:
        return self.settings['indicators']['avsl_configs']


    def load_bollinger_bands_configs(self) -> dict:
        return self.settings['indicators']['bollinger_bands_settings']


    def load_alma_configs(self) -> dict:
        return self.settings['indicators']['alma_configs']


    def load_rsi_clouds_configs(self) -> dict:
        return self.settings['indicators']['rsi_clouds_configs']


    def load_stoch_rsi_configs(self) -> dict:
        return self.settings['indicators']['stoch_rsi_configs']


    def load_vpci_configs(self) -> dict:
        return self.settings['indicators']['vpci_configs']


    def load_adx_configs(self) -> dict:
        return self.settings['indicators']['adx_configs']


    def load_kama_configs(self) -> dict:
        return self.settings['indicators']['kama_configs']


    def load_mesa_adaptive_ma_configs(self) -> dict:
        return self.settings['indicators']['mesa_adaptive_ma_configs']


    def load_zigzag_configs(self) -> dict:
        return self.settings['indicators']['zigzag_configs']


    def load_vwma_adx_configs(self) -> dict:
        return self.settings['indicators']['vwma_configs']


    def load_crsi_configs(self) -> dict:
        return self.settings['indicators']['crsi_configs']


    def load_baes_ultimate_osc_configs(self) -> dict:
        return self.settings['indicators']['bayes_ultimate_osc_configs']
