import time, hmac, hashlib, base64
import aiohttp
from typing import Optional, Union, Dict
import okx.Account as Account
import okx.MarketData as MarketData
import pandas as pd
from datasets.RedisCache import RedisCache
from utils.LoggingFormater import MultilineJSONFormatter
from docx import Document
from utils.DataFrameUtils import prepare_many_data_to_append_db, create_dataframe, validate_get_data_params
from utils.CustomDecorators import retry


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
        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)
        self.format = MultilineJSONFormatter()

    @retry(max_retries=5)
    def get_market_data(self, lengths:Union[int, str] = None, load_data_after:Optional[str]=None, load_data_before:Optional[str]=None) -> Optional[pd.DataFrame]:
        params = validate_get_data_params(lengths, load_data_before, load_data_after)
        result = self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        if result['code'] != '0':
            raise ValueError(f'Get market data, code: {result['code']}')
        return result

    @retry(max_retries=5)
    def check_balance(self) -> float:
        result = self.accountAPI.get_account_balance()
        if result['code'] != '0':
            raise ValueError(f'Check balance, code: {result['code']}')
        return float(result["data"][0]["details"][0]["availBal"])


    # Установка левериджа кросс позиций для отдельного инструмента
    @retry(max_retries=5)
    def set_leverage_inst(self) -> None:
        result = self.accountAPI.set_leverage(
            instId=self.instId,
            lever=self.leverage,
            mgnMode=self.mgnMode #cross или isolated
        )
        if result["code"] != "0":
            raise ValueError(f'Set leverage for instrument, code: {result['code']}')
        return self.leverage


    # Установка левериджа для \изолированых позиций для шорт и лонг
    @retry(max_retries=5)
    def set_leverage_short_long(self, posSide:str) -> None:
        result = self.accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            posSide = posSide,
            mgnMode = self.mgnMode
        )
        if result['code'] != '0':
            raise ValueError(f'Set leverage for short or long positions, code: {result['code']}')


    # Установка режима торговли
    @retry(max_retries=5)
    def set_trading_mode(self) -> None:
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        if result['code'] != '0':
            raise ValueError(f'Set trading mode, code: {result['code']}')


    @retry(max_retries=5)
    def check_instrument_info(self, instId:str) -> None:
        result = self.marketDataAPI.get_ticker(instId=instId)
        if result['code'] != '0':
            raise ValueError(f'check instrument info, code: {result['code']}')
        
        

    # Встроить в какой-нибудь синк майн
    @retry(max_retries=5)
    def check_contract_price(self, save:Optional[bool]=None) -> None:
        result = self.accountAPI.get_instruments(instType="SWAP")
        if result['code'] != '0':
            raise ValueError(f'Check contract price, code: {result['code']}')
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)


    @retry(max_retries=5)
    def check_contract_price_cache(self, instId:str) -> float:
        result = super().load_message_from_cache()
        return float(next(
                (
                    instrument['ctVal']
                    for instrument in result['data']
                    if instrument['instId'] == instId
                ),
                None,
            ))


    @retry(max_retries=5)
    def check_instrument_price(self, instId:str) -> float:
        result = self.marketDataAPI.get_ticker(instId)
        if result['code'] != '0':
            raise ValueError(f'Check instrument price, code: {result['code']}')
        return float(result['data'][0]['last'])
    
    
    async def get_last_price(self, instId:str) -> float:
        timestamp = f'{int(time.time() * 1000)}'
        request_path = f'/api/v5/market/ticker?instId={instId}'
        body = ''
        message = f'{timestamp}GET{request_path}{body}'
        signature = base64.b64encode(hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).digest()).decode()
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': "application/json"
        }
        url = f'https://www.okx.com/api/v5/market/ticker?instId={instId}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await float(response.json()['data'][0]['last'])