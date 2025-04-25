#libs
from typing import Optional, Union
from datetime import datetime, timedelta
#functions
from api.base.requests_links import TRADE
from api.base.client_async import ClientAsync
from api.okx_info_async import OKXInfoFunctionsAsync
from configs.load_settings import ConfigsProvider
#utils
from baselogs.custom_decorators import retry_on_exception_async
from baselogs.custom_decorators import log_exceptions_async
from baselogs.custom_logger import create_logger


logger = create_logger('TradeRequestsAsync')

class OKXTradeRequestsAsync(ClientAsync):
    def __init__(
            self,
            instId:Optional[str]=None, size:Optional[float]=None,
            posSide:Optional[str]=None, tpPrice:Optional[float]=None,
            slPrice:Optional[float]=None
            ):
        init_url = 'https://www.okx.com'
        settings = ConfigsProvider()
        api_settings = settings.load_api_configs()
        self.api_key, self.secret_key, self.passphrase, self.flag = api_settings['api_key'], api_settings['secret_key'], api_settings['passphrase'], api_settings['flag']
        user_settings = settings.load_user_configs()
        self.mgnMode, self.leverage, self.risk = user_settings['mgnMode'], user_settings['leverage'], user_settings['risk']
        ClientAsync.__init__(self, init_url, self.api_key, self.secret_key, self.passphrase, self.flag, self.debug, logger)
        self.instId, self.size, self.posSide, self.tpPrice, self.slPrice = instId, size, posSide, tpPrice, slPrice
        self.empty = ''


    @log_exceptions_async(logger)
    async def __get_tp_sl_order_params(
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

    @log_exceptions_async(logger)
    async def __get_tp_sl_order_change_params(
        self, orderId:str, slTriggerPx:str='', slTriggerPxType:str='',
        tpTriggerPx:str='', tpTriggerPxType:str='') -> dict:
        return {
            'instId': self.instId, 'algoId': orderId, 'algoClOrdId': self.empty, 'cxlOnFail': self.empty,
            'reqId': self.empty, 'newSz': self.empty, 'newTpTriggerPx': tpTriggerPx, 'newTpOrdPx': self.empty,
            'newSlTriggerPx': slTriggerPx, 'newSlOrdPx': self.empty, 'newTpTriggerPxType': tpTriggerPxType,
            'newSlTriggerPxType': slTriggerPxType
        }

    @log_exceptions_async(logger)
    async def __get_order_params(self, side:str, ordType:str, price:Union[int, float]='') -> dict:
        return {
            'instId': self.instId, 'tdMode': self.mgnMode, 'side': side, 'ordType': ordType,
            'sz': str(self.size), 'ccy': self.empty, 'clOrdId': self.empty, 'tag': self.empty,
            'posSide': self.posSide, 'px': price, 'reduceOnly': self.empty, 'tgtCcy': self.empty,
            'tpTriggerPx': self.empty, 'tpOrdPx': self.empty, 'slTriggerPx': self.empty,
            'slOrdPx': self.empty, 'tpTriggerPxType': self.empty, 'slTriggerPxType': self.empty,
            'quickMgnType': self.empty, 'stpId': self.empty, 'stpMode': self.empty, 'attachAlgoOrds': None
        }


    async def __check_pos_side(self):
        if self.posSide == 'long':
                    side = 'sell'
        elif self.posSide == 'short':
                    side = 'buy'
        return side


    @retry_on_exception_async(logger)
    async def construct_market_order(self) -> dict:
        side = await self.__check_pos_side
        params = await self.__get_order_params(side=side, ordType='market')
        method = TRADE['construct_market_order']['method']
        request_path = TRADE['construct_market_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        outTime = str(datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3))
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}



    @retry_on_exception_async(logger)
    async def construct_stoploss_order(self) -> str:
        side = await self.__check_pos_side 
        params = await self.__get_tp_sl_order_params(side=side, ordType='conditional', slOrdPx='-1',slTriggerPxType='mark', slTriggerPx=str(self.slPrice))
        method = TRADE['construct_stoploss_order']['method']
        request_path = TRADE['construct_stoploss_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result['data'][0]['ordId']


    @retry_on_exception_async(logger)
    async def change_stoploss_order(self, price:Union[float, int], orderId:str) -> None:
        # sourcery skip: inline-immediately-returned-variable
        params = await self.__get_tp_sl_order_change_params(orderId=orderId, slTriggerPx=str(price), slTriggerPxType='mark')
        method = TRADE['change_stoploss_order']['method']
        request_path = TRADE['change_stoploss_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result


    @retry_on_exception_async(logger)
    async def construct_takeprofit_order(self) -> str:
        side = await self.__check_pos_side()
        params = await self.__get_tp_sl_order_params(
            side=side, ordType='conditional', tpOrdPx='-1',
            tpTriggerPxType='mark', tpTriggerPx=str(self.slPrice)
        )
        method = TRADE['construct_takeprofit_order']['method']
        request_path = TRADE['construct_takeprofit_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return str(result['data'][0]['ordId'])


    @retry_on_exception_async(logger)
    async def change_takeprofit_order(self, price:Union[float, int], orderId:str) -> dict:
        # sourcery skip: inline-immediately-returned-variable
        params = await self.__get_tp_sl_order_change_params(orderId=orderId, tpTriggerPx=str(price), tpTriggerPxType='mark')
        method = TRADE['change_takeprofit_order']['method']
        request_path = TRADE['change_takeprofit_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result


    @retry_on_exception_async(logger)
    async def construct_limit_order(self, price:Union[float, int]) -> dict:
        side = await self.__check_pos_side()
        params = await self.__get_order_params(side=side, ordType='limit', price=price)
        method = TRADE['construct_limit_order']['method']
        request_path = TRADE['construct_limit_order']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return {
            'order_id': result["data"][0]["ordId"],
            'outTime': datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        }


    @log_exceptions_async(logger)
    async def calculate_posSize_async(self) -> float:
        return ((await OKXInfoFunctionsAsync().get_account_balance_async())\
            * self.leverage * self.risk) / self.slPrice


    @retry_on_exception_async(logger)
    async def check_position(self, ordId) -> dict:
        params = {'instId': self.instId, 'ordId': ordId, 'clOrdId': self.empty}
        method = TRADE['check_position']['method']
        request_path = TRADE['check_position']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result['data'][0]['avgPx']


    @retry_on_exception_async(logger)
    async def get_all_order_list(self) -> dict:
        # sourcery skip: inline-immediately-returned-variable
        params = {
            'instType': self.empty, 'uly': self.empty, 'instId': self.empty,
            'ordType': self.empty, 'state': self.empty, 'after': self.empty,
            'before': self.empty, 'limit': self.empty, 'instFamily': self.empty
        }
        method = TRADE['get_all_order_list']['method']
        request_path = TRADE['get_all_order_list']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result


    @retry_on_exception_async(logger)
    async def get_all_opened_positions(self) -> dict:
        # sourcery skip: inline-immediately-returned-variable
        params = {'instType': self.empty, 'instId': self.empty}
        method = TRADE['get_all_opened_positions']['method']
        request_path = TRADE['get_all_opened_positions']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result


    @retry_on_exception_async(logger)
    async def get_history(self, instType:str='SWAP', after:str='', before:str='', limit:int='', instId:str='') -> dict:
        # sourcery skip: inline-immediately-returned-variable
        params = {
            'instType': instType, 'uly': self.empty, 'instId': instId,
            'ordId': self.empty, 'after': after, 'before': before,'limit': limit,
            'instFamily': self.empty,'begin': self.empty, 'end': self.empty
            }
        method = TRADE['get_history']['method']
        request_path = TRADE['get_history']['url']
        result = await self._request_with_params_async(request_path, params, method)
        return result