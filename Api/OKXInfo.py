#libs
from typing import Optional, Union
import okx.Account as Account, okx.MarketData as MarketData, pandas as pd
#configs
from Configs.LoadSettings import LoadUserSettingData
#cache
from Cache.RedisCache import RedisCache
#utils
from DataSets.Utils.DataFrameUtils import validate_get_data_params
from Logs.CustomDecorators import retry_on_exception
from Logs.CustomLogger import create_logger
from Logs.CustomLogger import MultilineJSONFormatter
from docx import Document


logger = create_logger('OKXInfo')


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class OKXInfoFunctions(RedisCache):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None
        ):
        self.key = 'contracts_prices'
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        api_settings = LoadUserSettingData().load_api_setings()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = LoadUserSettingData().load_user_settings()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        self.format = MultilineJSONFormatter()


    def __create_accountAPI(self):
        self.accountAPI = Account.AccountAPI(
            self.api_key, self.secret_key,
            self.passphrase, False, self.flag
        )


    def __create_marketAPI(self):
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)


    def __check_result(self, result):
        if result['code'] != '0':
            raise ValueError(f'Get market data, code: {result['code']}')


    @retry_on_exception()
    def get_market_data(
        self, lengths:Union[int, str] = None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ) -> Optional[pd.DataFrame]:
        params = validate_get_data_params(lengths, load_data_before, load_data_after)
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


    @retry_on_exception()
    def check_balance(self) -> float:
        self.__create_accountAPI()
        result = self.accountAPI.get_account_balance()
        self.__check_result(result)
        return float(result["data"][0]["details"][0]["availBal"])


    # Установка левериджа кросс позиций для отдельного инструмента
    @retry_on_exception()
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
    @retry_on_exception()
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
    @retry_on_exception()
    def set_trading_mode(self) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        self.__check_result(result)


    @retry_on_exception()
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


    @retry_on_exception()
    def check_instrument_price(self, instId:str) -> float:
        self.__create_marketAPI()
        result = self.marketDataAPI.get_ticker(instId)
        self.__check_result(result)
        return float(result['data'][0]['last'])


