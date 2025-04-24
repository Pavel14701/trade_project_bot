#libs
from typing import Optional, Union
from sqlalchemy.orm import sessionmaker
import okx.Account as Account, okx.MarketData as MarketData, pandas as pd
#configs
from configs.load_settings import ConfigsProvider
#cache
from cache.redis_cache import RedisCache
from datasets.database import DataAllDatasets
#utils
from docx import Document
from datasets.utils.dataframe_utils import validate_get_data_params
from baselogs.custom_decorators import retry_on_exception
from baselogs.custom_logger import create_logger
from baselogs.custom_logger import MultilineJSONFormatter
logger = create_logger('OKXInfo')
"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""
class OKXInfoFunctions(RedisCache, DataAllDatasets):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None, Session:Optional[sessionmaker]=None,
        classes_dict:Optional[dict]=None
        ):
        settings = ConfigsProvider()
        print(settings)
        self.key = 'contracts_prices'
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        api_settings = settings.load_api_configs()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = settings.load_user_configs()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        self.format = MultilineJSONFormatter()
        DataAllDatasets.__init__(self, Session, classes_dict, instId, timeframe)
        



    def __create_accountAPI(self) -> None:
        self.accountAPI = Account.AccountAPI(
            self.api_key, self.secret_key,
            self.passphrase, False, self.flag
        )


    def __create_marketAPI(self) -> None:
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)
        
    def __check_result(self, result) -> None:
        if result['code'] != '0':
            raise ValueError(f'Get market data, code: {result['code']}')


    @retry_on_exception(logger)
    def get_market_data(
        self, lengths:Union[int, str, None] = None, load_data_after:Union[str, int]=None,
        load_data_before:Union[str, int]=None,
        use_class_length:Optional[bool]=None) -> dict:
        if lengths is None and use_class_length:
            lengths = self.lenghts
        params = validate_get_data_params(False, lengths, load_data_before, load_data_after)
        self.__create_marketAPI()
        result = self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def get_market_data_history(
        self, lengths:Union[int, str, None] = None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ) -> dict:
        params = validate_get_data_params(True, lengths, load_data_before, load_data_after)
        self.__create_marketAPI()
        result = self.marketDataAPI.get_history_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        self.__check_result(result)
        return result



    @retry_on_exception(logger)
    def check_balance(self) -> float:
        self.__create_accountAPI()
        result = self.accountAPI.get_account_balance()
        self.__check_result(result)
        return float(result["data"][0]["details"][0]["availBal"])


    # Установка левериджа кросс позиций для отдельного инструмента
    @retry_on_exception(logger)
    def set_leverage_inst(self) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId=self.instId,
            lever=self.leverage,
            mgnMode=self.mgnMode #cross или isolated
        )
        self.__check_result(result)
        return self.leverage


    # Установка левериджа для \изолированых позиций для шорт и лонг
    @retry_on_exception(logger)
    def set_leverage_short_long(self, posSide:str) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            posSide = posSide,
            mgnMode = self.mgnMode
        )
        self.__check_result(result)


    # Установка режима торговли
    @retry_on_exception(logger)
    def set_trading_mode(self) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        self.__check_result(result)


    @retry_on_exception(logger)
    def check_contract_price(self, save:Optional[bool]=None) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.get_instruments(instType="SWAP")
        self.__check_result(result)
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)


    def check_contract_price_cache(self, instId:str) -> float:
        result = self.load_message_from_cache()
        return float(next((instrument['ctVal'] for instrument in result['data']\
            if instrument['instId'] == instId),None,))


    @retry_on_exception(logger)
    def check_instrument_price(self, instId:str) -> float:
        self.__create_marketAPI()
        result = self.marketDataAPI.get_ticker(instId)
        self.__check_result(result)
        return float(result['data'][0]['last'])