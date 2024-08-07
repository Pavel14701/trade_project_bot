from typing import Optional, Union
import okx.Account as Account, okx.MarketData as MarketData, pandas as pd
from docx import Document
from datasets.RedisCache import RedisCache
from utils.LoggingFormater import MultilineJSONFormatter
from User.LoadSettings import LoadUserSettingData
from utils.DataFrameUtils import validate_get_data_params
from utils.CustomDecorators import retry_on_exception

"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class UserInfo(RedisCache):
    def __init__(
        self, instId=None|str, timeframe:str=None, lenghts=None|int, 
        load_data_after:str=None, load_data_before:str=None
        ):
        super().__init__(key='contracts_prices')
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        api_settings = LoadUserSettingData.load_api_setings()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = LoadUserSettingData.load_user_settings()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        self.format = MultilineJSONFormatter()


    def create_accountAPI(self):
        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    def create_marketAPI(self):
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)


    def check_result(self, result):
        if result['code'] != '0':
            raise ValueError(f'Get market data, code: {result['code']}')


    @retry_on_exception(max_retries=10, delay=3)
    def get_market_data(self, lengths:Union[int, str] = None, load_data_after:Optional[str]=None, load_data_before:Optional[str]=None) -> Optional[pd.DataFrame]:
        params = validate_get_data_params(lengths, load_data_before, load_data_after)
        self.create_marketAPI()
        result = self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        self.check_result(result)
        return result

    @retry_on_exception(max_retries=10, delay=3)
    def check_balance(self) -> float:
        self.create_accountAPI()
        result = self.accountAPI.get_account_balance()
        self.check_result(result)
        return float(result["data"][0]["details"][0]["availBal"])


    # Установка левериджа кросс позиций для отдельного инструмента
    @retry_on_exception(max_retries=10, delay=3)
    def set_leverage_inst(self) -> None:
        self.create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId=self.instId,
            lever=self.leverage,
            mgnMode=self.mgnMode #cross или isolated
        )
        self.check_result(result)
        return self.leverage


    # Установка левериджа для \изолированых позиций для шорт и лонг
    @retry_on_exception(max_retries=10, delay=3)
    def set_leverage_short_long(self, posSide:str) -> None:
        self.create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            posSide = posSide,
            mgnMode = self.mgnMode
        )
        self.check_result(result)


    # Установка режима торговли
    @retry_on_exception(max_retries=10, delay=3)
    def set_trading_mode(self) -> None:
        self.create_accountAPI()
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        self.check_result(result)


    @retry_on_exception(max_retries=10, delay=3)
    def check_contract_price(self, save:Optional[bool]=None) -> None:
        self.create_accountAPI()
        result = self.accountAPI.get_instruments(instType="SWAP")
        self.check_result(result)
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)


    def check_contract_price_cache(self, instId:str) -> float:
        result = super().load_message_from_cache()
        return float(next((instrument['ctVal'] for instrument in result['data'] if instrument['instId'] == instId),None,))


    @retry_on_exception(max_retries=10, delay=3)
    def check_instrument_price(self, instId:str) -> float:
        self.create_marketAPI()
        result = self.marketDataAPI.get_ticker(instId)
        self.check_result(result)
        return float(result['data'][0]['last'])


