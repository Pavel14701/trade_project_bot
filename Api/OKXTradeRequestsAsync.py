#libs
import aiohttp, json
from typing import Optional, Union
from datetime import datetime, timedelta
#functios
from Api.OKXInfoAsync import OKXInfoFunctionsAsync
from Configs.LoadSettings import LoadUserSettingData
#utils
from Logs.CustomDecorators import retry_on_exception_async
from Logs.CustomDecorators import log_exceptions_async
from Logs.CustomLogger import create_logger


logger = create_logger('TradeRequestsAsync')
retry_settings = LoadUserSettingData().load_retry_requests_configs()
max_retries = retry_settings['max_retries']
delay = retry_settings['delay']


class OKXTradeRequestsAsync:
    def __init__(
            self,
            instId:Optional[str]=None, size:Optional[float]=None,
            posSide:Optional[str]=None, tpPrice:Optional[float]=None,
            slPrice:Optional[float]=None
            ):
        api_settings = LoadUserSettingData().load_api_setings()
        self.base_url = 'https://www.okx.com'
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = LoadUserSettingData().load_user_settings()
        self.mgnMode = user_settings['mgnMode']
        self.leverage = user_settings['leverage']
        self.risk = user_settings['risk']
        self.instId = instId
        self.size = size
        self.posSide = posSide #long or short
        self.tpPrice = tpPrice
        self.slPrice = slPrice
        self.empty = ''


    @log_exceptions_async(logger)
    async def __make_request(self, sign:bool, request_path:str, body:str, method:str) -> dict:
        headers = await LoadUserSettingData().create_headers(sign, request_path, body, method, self.flag)
        if self.debug:
            print(f'{self.base_url}{request_path}')
            print(headers)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}{request_path}', headers=headers) as response:
                result = await response.json()
                if result['code'] != '0':
                    raise ValueError(f'Construct market order, code: {result['code']}')
                return result


    @log_exceptions_async(logger)
    async def get_tp_sl_order_params(
        self, side:str, ordType:str, slOrdPx:str='', slTriggerPxType:str='',
        slTriggerPx:str='', tpOrdPx:str='', tpTriggerPxType:str='',
        tpTriggerPx:str=''
        ) -> dict:
        return json.dumps({
            'instId': self.instId, 'tdMode': self.mgnMode, 'side': side, 'ordType': ordType,
            'sz': str(self.size), 'ccy': self.empty, 'posSide': self.posSide, 'reduceOnly': self.empty, 
            'tpTriggerPx': tpTriggerPx, 'tpOrdPx': tpOrdPx, 'slTriggerPx': slTriggerPx, 'slOrdPx': slOrdPx,
            'triggerPx': self.empty, 'orderPx': self.empty, 'tgtCcy': self.empty, 'pxVar': self.empty,
            'szLimit': self.empty, 'pxLimit': self.empty, 'timeInterval': self.empty, 'pxSpread': self.empty,
            'tpTriggerPxType': tpTriggerPxType, 'slTriggerPxType': slTriggerPxType, 'callbackRatio': self.empty,
            'callbackSpread': self.empty, 'activePx': self.empty, 'tag': self.empty, 'triggerPxType': self.empty,
            'closeFraction': self.empty, 'quickMgnType': self.empty, 'algoClOrdId': self.empty
        })

    @log_exceptions_async(logger)
    async def __get_tp_sl_order_change_params(
        self, orderId:str, slTriggerPx:str='', slTriggerPxType:str='',
        tpTriggerPx:str='', tpTriggerPxType:str=''):
        return json.dumps({
            'instId': self.instId, 'algoId': orderId, 'algoClOrdId': self.empty, 'cxlOnFail': self.empty,
            'reqId': self.empty, 'newSz': self.empty, 'newTpTriggerPx': tpTriggerPx, 'newTpOrdPx': self.empty,
            'newSlTriggerPx': slTriggerPx, 'newSlOrdPx': self.empty, 'newTpTriggerPxType': tpTriggerPxType,
            'newSlTriggerPxType': slTriggerPxType
        })

    @log_exceptions_async(logger)
    async def __get_order_params(self, side:str, ordType:str, price:Union[int, float]='') -> dict:
        return json.dumps({
            'instId': self.instId, 'tdMode': self.mgnMode, 'side': side, 'ordType': ordType,
            'sz': str(self.size), 'ccy': self.empty, 'clOrdId': self.empty, 'tag': self.empty,
            'posSide': self.posSide, 'px': price, 'reduceOnly': self.empty, 'tgtCcy': self.empty,
            'tpTriggerPx': self.empty, 'tpOrdPx': self.empty, 'slTriggerPx': self.empty,
            'slOrdPx': self.empty, 'tpTriggerPxType': self.empty, 'slTriggerPxType': self.empty,
            'quickMgnType': self.empty, 'stpId': self.empty, 'stpMode': self.empty, 'attachAlgoOrds': None
        })


    async def __check_pos_side(self):
        if self.posSide == 'long':
                    side = 'sell'
        elif self.posSide == 'short':
                    side = 'buy'
        return side


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def construct_market_order_async(self) -> dict:
        sign = True
        side = await self.__check_pos_side
        body= await self.__get_order_params(side=side, ordType='market')
        method = 'POST'
        request_path = '/api/v5/trade/order'
        result = await self.__make_request(sign, request_path, body, method)
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def construct_stoploss_order_async(self) -> str:
        sign = True
        side = await self.__check_pos_side 
        body = await self.get_tp_sl_order_params(
            side=side, ordType='conditional', slOrdPx='-1',
            slTriggerPxType='mark', slTriggerPx=str(self.slPrice)
        )
        method = 'POST'
        request_path = '/api/v5/trade/order-algo'
        result = await self.__make_request(sign, request_path, body, method)
        return result['data'][0]['ordId']


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def change_stoploss_order_async(self, price:Union[float, int], orderId:str) -> None:
        sign = True
        body = await self.__get_tp_sl_order_change_params(orderId=orderId, slTriggerPx=str(price), slTriggerPxType='mark')
        method = 'POST'
        request_path =  '/api/v5/trade/amend-algos'
        return await self.__make_request(sign, request_path, body, method)


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def construct_takeprofit_order_async(self) -> str:
        sign = True
        side = await self.__check_pos_side()
        body = await self.get_tp_sl_order_params(
            side=side, ordType='conditional', tpOrdPx='-1',
            tpTriggerPxType='mark', tpTriggerPx=str(self.slPrice)
        )
        method = 'POST'
        request_path = '/api/v5/trade/order-algo'
        return await self.__make_request(sign, request_path, body, method)['data'][0]['ordId']


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def change_takeprofit_order_async(self, price:Union[float, int], orderId:str) -> None:
        sign = True
        body = await self.__get_tp_sl_order_change_params(orderId=orderId, tpTriggerPx=str(price), tpTriggerPxType='mark')
        method = 'POST'
        request_path =  '/api/v5/trade/amend-algos'
        return await self.__make_request(sign, request_path, body, method)


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def construct_limit_order_async(self, price:Union[float, int]) -> dict:
        sign = True
        side = await self.__check_pos_side()
        body = await self.__get_order_params(side=side, ordType='limit', price=price)
        method = 'POST'
        request_path = '/api/v5/trade/order'
        result = await self.__make_request(sign, request_path, body, method)
        return {
            'order_id': result["data"][0]["ordId"],
            'outTime': datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        }


    @log_exceptions_async(logger)
    async def calculate_posSize_async(self) -> float:
        return ((await OKXInfoFunctionsAsync().get_account_balance_async())\
            * self.leverage * self.risk) / self.slPrice


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def check_position_async(self, ordId) -> dict:
        sign = True
        body = json.dumps({'instId': self.instId, 'ordId': ordId, 'clOrdId': self.empty})
        method = 'GET'
        request_path = '/api/v5/trade/order'
        return await float(self.__make_request(sign, request_path, body, method))['data'][0]['avgPx']


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def get_all_order_list_async(self) -> dict:
        sign = True
        body = json.dumps({
            'instType': self.empty, 'uly': self.empty, 'instId': self.empty,
            'ordType': self.empty, 'state': self.empty, 'after': self.empty,
            'before': self.empty, 'limit': self.empty, 'instFamily': self.empty
        })
        method = 'GET'
        request_path = '/api/v5/trade/orders-pending'
        return await self.__make_request(sign, request_path, body, method)


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def get_all_opened_positions_async(self) -> dict:
        sign = True
        body = json.dumps({'instType': self.empty, 'instId': self.empty})
        method = 'GET'
        request_path = '/api/v5/account/positions'
        return await self.__make_request(sign, request_path, body, method)


    @log_exceptions_async(logger)
    @retry_on_exception_async(max_retries, delay)
    async def get_history_async(self, instType:str='SWAP', after:str='', before:str='', limit:int='', instId:str='') -> dict:
        sign = True
        body = json.dumps({
            'instType': instType, 'uly': self.empty, 'instId': instId,
            'ordId': self.empty, 'after': after, 'before': before,'limit': limit,
            'instFamily': self.empty,'begin': self.empty, 'end': self.empty
            })
        method = 'GET'
        request_path = '/api/v5/trade/fills'
        return await self.__make_request(sign, request_path, body, method)