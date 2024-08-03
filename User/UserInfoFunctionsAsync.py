import json, aiohttp, aiofiles
from typing import Optional
from docx import Document
from User.LoadSettings import LoadUserSettingData
from datasets.AioRedisCache import AioRedisCache
from utils.DataFrameUtils import async_generator
from utils.CustomDecorators import retry_on_exception_async
import asyncio

retry_settings = LoadUserSettingData.load_retry_requests_configs()
max_retries = retry_settings['max_retries']
delay = retry_settings['delay']


class UserInfoAsync(AioRedisCache):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None, debug:Optional[bool]=True
        ):
        super(AioRedisCache).__init__(key='contracts_prices')
        self.debug = debug
        api_settings = LoadUserSettingData.load_api_setings()
        self.secret_key = api_settings['secret_key']
        self.api_key = api_settings['api_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        self.base_url = 'https://www.okx.com'
        user_settings = LoadUserSettingData.load_user_settings()
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


    async def make_request(self, request_path:Optional[str], headers:Optional['dict']):
        if self.debug:
            print(f'{self.base_url}{request_path}')
            print(headers)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}{request_path}', headers=headers) as response:
                result = await response.json()
                if result['code'] != 0:
                    raise ValueError(f'Check balance, code: {result['code']}')
                print(result)
                return result


    async def save_swap_docx(self, result:Optional[dict], filename:Optional[str]):
        doc = Document()
        doc.add_paragraph(str(result))
        temp_filename = 'temp.docx'
        doc.save(temp_filename)
        async with aiofiles.open(temp_filename, 'rb') as temp_file:
            content = await temp_file.read()
        async with aiofiles.open(filename, 'wb') as target_file:
            await target_file.write(content)


    @retry_on_exception_async(max_retries, delay)
    async def get_candlesticks_async(self) -> dict:
        request_path = f'/api/v5/market/candles?instId={self.instId}&bar={self.timeframe}&limit={self.lenghts}'
        if self.load_data_after:
            request_path += f'&after={self.load_data_after}'
        if self.load_data_before:
            request_path += f'&before={self.load_data_before}'
        method = 'GET'
        body = ''
        headers = await LoadUserSettingData.create_headers(True, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        return result['data']


    @retry_on_exception_async(max_retries, delay)
    async def get_account_balance(self) -> float:
        request_path = '/api/v5/account/balance'
        method = 'GET'
        body = ''
        headers = await LoadUserSettingData.create_headers(True, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        return float(result["data"][0]["details"][0]["availBal"])


    @retry_on_exception_async(max_retries, delay)
    async def set_leverage_inst(self, posSide:Optional[str], ccy:Optional[str]=None):
        if ccy is None:
            ccy = '' 
        params = {'lever': self.leverage, 'mgnMode': self.mgnMode, 'instId': self.instId, 'ccy': ccy , 'posSide': posSide}
        body = json.dumps(params)
        request_path =  '/api/v5/account/set-leverage'
        method = 'POST'
        headers = await LoadUserSettingData.create_headers(True, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        return self.leverage


    @retry_on_exception_async(max_retries, delay)
    async def check_contract_price_async(self, filename:Optional[str]='SWAPINFO.docx', save:Optional[bool]=None) -> None:
        params = {'instType': 'SWAP', 'ugly': '', 'instFamily': '', 'instId': ''}
        body = json.dumps(params)
        request_path = '/api/v5/account/instruments'
        method = 'GET'
        headers = await LoadUserSettingData.create_headers(True, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if save:
            await self.save_swap_docx(result, filename)
        elif save == False:
            await self.async_send_redis_command(result, self.key)


    async def check_contract_price_cache_async(self, instId:str) -> float:
        result = await self.async_load_message_from_cache()
        async for instrument in async_generator(result['data']):
            if instrument['instId'] == instId:
                return float(instrument['ctVal'])
        raise ValueError('Object not founded')

    @retry_on_exception_async(max_retries, delay)
    async def get_last_price_async(self, instId:str) -> float:
        request_path = f'/api/v5/market/ticker?instId={instId}'
        method = 'GET'
        body = ''
        headers = await LoadUserSettingData.create_headers(True, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        return float(result['data'][0]['last'])


'''
# Пример использования
async def foo(): 
    market_data_api = UserInfoAsync('BTC-USDT-SWAP', '1m', 300)
    candlesticks = await market_data_api.get_candlesticks_async()
    print(candlesticks)
    balance = await market_data_api.get_account_balance()
    print(balance)


if __name__ =='__main__':
    asyncio.run(foo())
'''
