#libs
from typing import Optional
#functions
from api.base.client_async import ClientAsync
from api.base.requests_links import INFO
from cache.aioredis_cache import AioRedisCache
from configs.load_settings import ConfigsProvider
#utils
from api.utils.api_utils import ApiUtilsAsync
from docx import Document
from datasets.utils.dataframe_utils_async import async_generator
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import retry_on_exception_async


logger = create_logger('OKXInfoAsync')


class OKXInfoFunctionsAsync(ClientAsync, AioRedisCache, ApiUtilsAsync):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None, debug:Optional[bool]=True, proxy:str=None
        ):
        self.debug = debug
        settings = ConfigsProvider()
        api_settings = settings.load_api_configs()
        self.secret_key = api_settings['secret_key']
        self.api_key = api_settings['api_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = settings.load_user_configs()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        ApiUtilsAsync.__init__(self, self.api_key, self.secret_key, self.passphrase, timeframe)
        self.validate_timeframe_format()
        init_url = 'https://www.okx.com'
        ClientAsync.__init__(
            self, init_url, self.api_key, self.secret_key,
            self.passphrase, self.flag, self.debug, proxy, logger
            )
        AioRedisCache.__init__(self, key='contracts_prices')
        self.instId = instId
        self.timeframe= timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before


    @retry_on_exception_async(logger)
    async def get_candlesticks(self) -> dict:
        params_dict = await self.validate_get_data_params_async(self.lenghts, self.load_data_before, self.load_data_after, self.timeframe)
        params = {
            'instId': self.instId, 'after': params_dict['after'],
            'before': params_dict['before'], 'bar': self.timeframe,
            'limit': params['limit']
        }
        request_path = INFO['get_candlesticks']['url']
        method = INFO['get_candlestics']['method']
        result = await self._request_with_params_async(request_path, params, method)
        return result['data']


    @retry_on_exception_async(logger)
    async def get_account_balance(self, ccy:Optional[str]=None) -> float:
        params = {}
        if ccy:
            params['ccy'] = ccy
        request_path = INFO['get_account_balance']['url']
        method = INFO['get_account_balance']['method']
        result = await self._request_with_params_async(request_path, params, method)
        return float(result["data"][0]["details"][0]["availBal"])


    @retry_on_exception_async(logger)
    async def set_leverage_inst(self) -> int:
        params = {'lever': self.leverage, 'mgnMode': self.mgnMode, 'instId': self.instId, 'ccy': '' , 'posSide': ''}
        request_path =  INFO['set_leverage_inst']['url']
        method = INFO['set_leverage_inst']['method']
        result = await self._request_with_params_async(request_path, params, method)
        return self.leverage


    @retry_on_exception_async(logger)
    async def set_leverage_short_long(self, posSide:Optional[str]):
        params = {'lever': self.leverage, 'mgnMode': self.mgnMode, 'instId': self.instId, 'ccy': '' , 'posSide': posSide}
        request_path =  INFO['set_leverage_short_long']['url']
        method = INFO['set_leverage_short_long']['method']
        result = await self._request_with_params_async(request_path, params, method)
        return self.leverage


    @retry_on_exception_async(logger)
    async def check_contract_price(self, instId:Optional[str]='', filename:Optional[str]='SWAPINFO.docx', save:Optional[bool]=None) -> None:
        params = {'instType': 'SWAP', 'ugly': ' ', 'instFamily': ' ', 'instId': instId}
        request_path = INFO['set_leverage_short_long']['url']
        method = INFO['set_leverage_short_long']['method']
        result = await self._request_with_params_async(request_path, params, method)
        if save:
            await self.save_swap_docx(result, filename)
        elif save == False:
            await self.async_send_redis_command(result, self.key)
        return result

    async def check_contract_price_cache_async(self, instId:str) -> float:
        result = await self.async_load_message_from_cache()
        async for instrument in async_generator(result['data']):
            return float(instrument['ctVal']) if instrument['instId'] == instId else None
        raise ValueError('Object not founded')

    @retry_on_exception_async(logger)
    async def get_last_price(self, instId:str) -> float:
        params = {'instId': instId}
        method = INFO['get_last_price']['method']
        request_path = INFO['get_last_price']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return float(result['data'][0]['last'])


    @retry_on_exception_async(logger)
    async def set_trading_mode(self) -> dict:
        # sourcery skip: inline-immediately-returned-variable
        params = {'posMode': 'long_short_mode'}
        method = INFO['set_trading_mode']['method']
        request_path = INFO['set_trading_mode']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result

"""
async def foo(): 
    market_data_api = OKXInfoFunctionsAsync('BTC-USDT-SWAP', '1m', 300)
    balance = await market_data_api.get_account_balance()
    print(f'\nbalance:\n{balance}\n')
    price = await market_data_api.check_contract_price()
    print(f'\nprice:{price}\n')


import asyncio
if __name__ =='__main__':
    asyncio.run(foo())
"""

