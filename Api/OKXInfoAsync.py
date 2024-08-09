#libs
import json, contextlib, aiofiles
from typing import Optional, Union
from datetime import datetime
#functions
from Api.Base.OKXClientAsync import OKXClientAsync
from Cache.AioRedisCache import AioRedisCache
from Configs.LoadSettings import LoadUserSettingData
#utils
from Api.Utils.Utils import ApiUtilsAsync
from docx import Document
from DataSets.Utils.DataFrameUtilsAsync import async_generator, async_validate_get_data_params
from BaseLogs.CustomLogger import create_logger
from BaseLogs.CustomDecorators import retry_on_exception_async



logger = create_logger('OKXInfoAsync')


class OKXInfoFunctionsAsync(OKXClientAsync, AioRedisCache, ApiUtilsAsync):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None, debug:Optional[bool]=True, proxy:str=None
        ):
        ApiUtilsAsync.__init__(self)
        settings = LoadUserSettingData()
        api_settings = settings.load_api_setings()
        self.secret_key = api_settings['secret_key']
        self.api_key = api_settings['api_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        self.debug = debug
        OKXClientAsync.__init__(self, self.api_key, self.secret_key, self.passphrase, self.flag, self.debug, proxy)
        AioRedisCache.__init__(self, key='contracts_prices')
        user_settings = settings.load_user_settings()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        self.instId = instId
        self.timeframe= timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before


    @retry_on_exception_async(logger=logger)
    async def get_candlesticks_async(self) -> dict:
        sign = True
        params = await self.validate_get_data_params_async(self.lenghts, self.load_data_before, self.load_data_after, self.timeframe)
        request_path = f'/api/v5/market/candles?instId={self.instId}&bar={self.timeframe}&limit={params}'
        if self.load_data_after:
            request_path += f'&after={params['after']}'
        if self.load_data_before:
            request_path += f'&before={params['before']}'
        method = 'GET'
        body = ''
        result = await self.make_request_async(sign, request_path, body, method)
        return result['data']


    @retry_on_exception_async(logger=logger)
    async def get_account_balance_async(self) -> float:
        sign = True
        request_path = '/api/v5/account/balance'
        method = 'GET'
        body = ''
        result = await self.make_request_async(sign, request_path, body, method)
        return float(result["data"][0]["details"][0]["availBal"])


    @retry_on_exception_async(logger=logger)
    async def set_leverage_inst_async(self) -> int:
        sign = True
        params = {'lever': self.leverage, 'mgnMode': self.mgnMode, 'instId': self.instId, 'ccy': '' , 'posSide': ''}
        body = json.dumps(params)
        request_path =  '/api/v5/account/set-leverage'
        method = 'POST'
        result = await self.make_request_async(sign, request_path, body, method)
        return self.leverage


    @retry_on_exception_async(logger=logger)
    async def set_leverage_short_long_async(self, posSide:Optional[str]):
        sign = True
        params = {'lever': self.leverage, 'mgnMode': self.mgnMode, 'instId': self.instId, 'ccy': '' , 'posSide': posSide}
        body = json.dumps(params)
        request_path =  '/api/v5/account/set-leverage'
        method = 'POST'
        result = await self.make_request_async(sign, request_path, body, method)
        return self.leverage


    @retry_on_exception_async(logger=logger)
    async def check_contract_price_async(self, instId:Optional[str]='', filename:Optional[str]='SWAPINFO.docx', save:Optional[bool]=None) -> None:
        sign = True
        params = {'instType': 'SWAP', 'ugly': '', 'instFamily': '', 'instId': f'{instId}'}
        print(params)
        body = json.dumps(params)
        request_path = '/api/v5/account/instruments'
        method = 'GET'
        result = await self.make_request_async(sign, request_path, body, method)
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

    @retry_on_exception_async(logger=logger)
    async def get_last_price_async(self, instId:str) -> float:
        sign = True
        request_path = f'/api/v5/market/ticker?instId={instId}'
        method = 'GET'
        body = ''
        result = await self.make_request_async(sign, request_path, body, method)
        return float(result['data'][0]['last'])


    @retry_on_exception_async(logger=logger)
    async def set_trading_mode_async(self) -> None:
        sign = True
        params = {'posMode': 'long_short_mode'}
        method = 'POST'
        body = json.dumps(params)
        request_path = '/api/v5/account/set-position-mode'
        return await self.make_request_async(sign, request_path, body, method)


async def foo(): 
    market_data_api = OKXInfoFunctionsAsync('BTC-USDT-SWAP', '1m', 300)
    balance = await market_data_api.get_account_balance_async()
    print(f'\nbalance:\n{balance}\n')
    price = await market_data_api.check_contract_price_async()
    print(f'\nprice:{price}\n')


import asyncio
if __name__ =='__main__':
    asyncio.run(foo())

