import aiohttp, json
from typing import Optional, Union
from datetime import datetime, timedelta
from User.LoadSettings import LoadUserSettingData
from User.UserInfoFunctionsAsync import UserInfoAsync
from utils.CustomDecorators import retry_on_exception_async

retry_settings = LoadUserSettingData.load_retry_requests_configs()
max_retries = retry_settings['max_retries']
delay = retry_settings['delay']


class OKXTradeRequestsAsync:
    def __init__(
            self,
            instId:Optional[str]=None, size:Optional[float]=None,
            posSide:Optional[str]=None, tpPrice:Optional[float]=None,
            slPrice:Optional[float]=None
            ):
        api_settings = LoadUserSettingData.load_api_setings()
        self.base_url = 'https://www.okx.com'
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = LoadUserSettingData.load_user_settings()
        self.mgnMode = user_settings['mgnMode']
        self.leverage = user_settings['leverage']
        self.risk = user_settings['risk']
        self.instId = instId
        self.size = size
        self.posSide = posSide #long or short
        self.tpPrice = tpPrice
        self.slPrice = slPrice
        self.empty = ''


    async def make_request(self, request_path:str, headers:dict) -> dict:
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


    async def get_tp_sl_order_params(
        self, side:str, ordType:str, slOrdPx:str='', slTriggerPxType:str='',
        slTriggerPx:str='', tpOrdPx:str='', tpTriggerPxType:str='',
        tpTriggerPx:str=''
        ) -> dict:
        return {
            'instId': self.instId, 'tdMode': self.mgnMode, 'side': side, 'ordType': ordType,
            'sz': str(self.size), 'ccy': self.empty, 'posSide': self.posSide, 'reduceOnly': self.empty, 
            'tpTriggerPx': tpTriggerPx, 'tpOrdPx': tpOrdPx, 'slTriggerPx': slTriggerPx, 'slOrdPx': slOrdPx,
            'triggerPx': self.empty, 'orderPx': self.empty, 'tgtCcy': self.empty, 'pxVar': self.empty,
            'szLimit': self.empty, 'pxLimit': self.empty, 'timeInterval': self.empty, 'pxSpread': self.empty,
            'tpTriggerPxType': tpTriggerPxType, 'slTriggerPxType': slTriggerPxType, 'callbackRatio': self.empty,
            'callbackSpread': self.empty, 'activePx': self.empty, 'tag': self.empty, 'triggerPxType': self.empty,
            'closeFraction': self.empty, 'quickMgnType': self.empty, 'algoClOrdId': self.empty
        }


    async def get_tp_sl_order_change_params(
        self, orderId:str, slTriggerPx:str='', slTriggerPxType:str='',
        tpTriggerPx:str='', tpTriggerPxType:str=''):
        return {
            'instId': self.instId, 'algoId': orderId, 'algoClOrdId': self.empty, 'cxlOnFail': self.empty,
            'reqId': self.empty, 'newSz': self.empty, 'newTpTriggerPx': tpTriggerPx, 'newTpOrdPx': self.empty,
            'newSlTriggerPx': slTriggerPx, 'newSlOrdPx': self.empty, 'newTpTriggerPxType': tpTriggerPxType,
            'newSlTriggerPxType': slTriggerPxType
        }


    async def get_order_params(self, side:str, ordType:str, price:Union[int, float]='') -> dict:
        return {
            'instId': self.instId, 'tdMode': self.mgnMode, 'side': side, 'ordType': ordType,
            'sz': str(self.size), 'ccy': self.empty, 'clOrdId': self.empty, 'tag': self.empty, 'posSide': self.posSide,
            'px': price, 'reduceOnly': self.empty, 'tgtCcy': self.empty, 'tpTriggerPx': self.empty, 'tpOrdPx': self.empty,
            'slTriggerPx': self.empty, 'slOrdPx': self.empty, 'tpTriggerPxType': self.empty, 'slTriggerPxType': self.empty,
            'quickMgnType': self.empty, 'stpId': self.empty, 'stpMode': self.empty, 'attachAlgoOrds': None
        }


    @retry_on_exception_async(max_retries, delay)
    async def construct_market_order_async(self) -> dict:
        sign = True
        if self.posSide == 'long':
                    side = 'buy'
        elif self.posSide == 'short':
                    side = 'sell'
        params = await self.get_order_params(side=side, ordType='market')
        body = json.dumps(params)
        method = 'POST'
        request_path = '/api/v5/trade/order'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Construct market order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    @retry_on_exception_async(max_retries, delay)
    async def construct_stoploss_order_async(self) -> str:
        sign = True
        if self.posSide == 'long':
            side = 'sell'
        elif self.posSide == 'short':
            side = 'buy'  
        params = await self.get_tp_sl_order_params(
            side=side, ordType='conditional', slOrdPx='-1',
            slTriggerPxType='mark', slTriggerPx=str(self.slPrice)
        )
        body = json.dumps(params)
        method = 'POST'
        request_path = '/api/v5/trade/order-algo'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Construct stoploss order, code: {result['code']}')
        return result['data'][0]['ordId']


    @retry_on_exception_async(max_retries, delay)
    async def change_stoploss_order_async(self, price:Union[float, int], orderId:str) -> None:
        sign = True
        params = await self.get_tp_sl_order_change_params(orderId=orderId, slTriggerPx=str(price), slTriggerPxType='mark')
        body = json.dumps(params)
        method = 'POST'
        request_path =  '/api/v5/trade/amend-algos'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Change stoploss order, code: {result['code']}')


    @retry_on_exception_async(max_retries, delay)
    async def construct_takeprofit_order_async(self) -> str:
        sign = True
        if self.posSide == 'long':
            side = 'sell'
        elif self.posSide == 'short':
            side = 'buy'  
        params = await self.get_tp_sl_order_params(
            side=side, ordType='conditional', tpOrdPx='-1',
            tpTriggerPxType='mark', tpTriggerPx=str(self.slPrice)
        )
        body = json.dumps(params)
        method = 'POST'
        request_path = '/api/v5/trade/order-algo'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Construct takeprofit order, code: {result['code']}')
        return result['data'][0]['ordId']


    @retry_on_exception_async(max_retries, delay)
    async def change_takeprofit_order_async(self, price:Union[float, int], orderId:str) -> None:
        sign = True
        params = await self.get_tp_sl_order_change_params(orderId=orderId, tpTriggerPx=str(price), tpTriggerPxType='mark')
        body = json.dumps(params)
        method = 'POST'
        request_path =  '/api/v5/trade/amend-algos'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Change takeprofit order, code: {result['code']}')


    @retry_on_exception_async(max_retries, delay)
    async def construct_limit_order_async(self, price:Union[float, int]) -> dict:
        sign = True
        if self.posSide == 'long':
                    side = 'buy'
        elif self.posSide == 'short':
                    side = 'sell'
        params = await self.get_order_params(side=side, ordType='limit', price=price)
        body = json.dumps(params)
        method = 'POST'
        request_path = '/api/v5/trade/order'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Construct limit order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    async def calculate_posSize_async(self) -> float:
        balance = await UserInfoAsync().get_account_balance_async()
        return (balance * self.leverage * self.risk) / self.slPrice


    @retry_on_exception_async(max_retries, delay)
    async def check_position_async(self, ordId) -> dict:
        sign = True
        params = {'instId': self.instId, 'ordId': ordId, 'clOrdId': self.empty}
        body = json.dumps(params)
        method = 'GET'
        request_path = '/api/v5/trade/order'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result['code'] != '0':
            raise ValueError(f'Construct limit order, code: {result['code']}')
        return float(result['data'][0]['avgPx'])


    @retry_on_exception_async(max_retries, delay)
    async def get_all_order_list_async(self) -> dict:
        sign = True
        params = {'instType': self.empty, 'uly': self.empty, 'instId': self.empty, 'ordType': self.empty, 'state': self.empty,
                  'after': self.empty, 'before': self.empty, 'limit': self.empty, 'instFamily': self.empty}
        body = json.dumps(params)
        method = 'GET'
        request_path = '/api/v5/trade/orders-pending'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result["code"] != "0":
            raise ValueError(f'Get all order list, code: {result['code']}')
        return result


    @retry_on_exception_async(max_retries, delay)
    async def get_all_opened_positions_async(self) -> dict:
        sign = True
        params = {'instType': self.empty, 'instId': self.empty}
        body = json.dumps(params)
        method = 'GET'
        request_path = '/api/v5/account/positions'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result["code"] != "0":
            raise ValueError(f'Get all opened positions, code: {result['code']}')
        return result


    @retry_on_exception_async(max_retries, delay)
    async def get_history_async(self, instType:str='SWAP', after:str='', before:str='', limit:int='', instId:str='') -> dict:
        sign = True
        params = {
            'instType': instType, 'uly': self.empty, 'instId': instId, 'ordId': self.empty, 'after': after,
            'before': before,'limit': limit, 'instFamily': self.empty,'begin': self.empty, 'end': self.empty
            }
        body = json.dumps(params)
        method = 'GET'
        request_path = '/api/v5/trade/fills'
        headers = await LoadUserSettingData.create_headers(sign, request_path, body, method, self.flag)
        result = await self.make_request(request_path, headers)
        if result["code"] != "0":
            raise ValueError(f'Get history from 3 days, code: {result['code']}')
        return result