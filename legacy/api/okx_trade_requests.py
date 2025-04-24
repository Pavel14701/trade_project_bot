#libs
from datetime import datetime, timedelta
from typing import Optional
import okx.Account as Account
import okx.Trade as Trade
#configs
from configs.load_settings import ConfigsProvider
#Api
from api.okx_info import OKXInfoFunctions
#utils
from baselogs.custom_decorators import retry_on_exception
from baselogs.custom_logger import create_logger


logger = create_logger('TradeRequests')


class OKXTradeRequests:
    def __init__(
            self, instId:Optional[str]=None, size:Optional[float]=None, posSide:Optional[str]=None,
            tpPrice:Optional[float]=None, slPrice:Optional[float]=None
            ):
        api_settings = ConfigsProvider().load_api_configs()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        self.instId = instId
        self.size = size
        user_settings = ConfigsProvider().load_user_configs()
        self.mgnMode = user_settings['mgnMode']
        self.leverage = user_settings['leverage']
        self.risk = user_settings['risk']
        self.posSide = posSide #long or short
        self.tpPrice = tpPrice
        self.slPrice = slPrice
        self.__create_account_api()
        self.__create_trade_api()


    def __create_account_api(self):
        self.accountApi = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    def __create_trade_api(self):
        self.tradeAPI = Trade.TradeAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    def __check_pos_side(self):
        if self.posSide == 'long':
                    side = 'sell'
        elif self.posSide == 'short':
                    side = 'buy'
        return side


    def __check_result(self, result:dict):
        if result['code'] != '0':
            raise ValueError(f'Construct market order, code: {result['code']}')


    @retry_on_exception(logger)
    def construct_market_order(self, side) -> dict:
        side = self.__check_pos_side()
        result = self.tradeAPI.place_order(
            instId=self.instId, tdMode=self.mgnMode,
            side=side, posSide=self.posSide,
            ordType="market", sz=str(self.size)
        )
        self.__check_result(result)
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    @retry_on_exception(logger)
    def construct_stoploss_order(self) -> str:
        side = self.__check_pos_side()
        result = self.tradeAPI.place_algo_order(
            instId=self.instId, tdMode=self.mgnMode, side=side,
            posSide=self.posSide, ordType='conditional', sz=str(self.size),
            slTriggerPx=str(self.slPrice), slOrdPx='-1', slTriggerPxType='last'
        )
        self.__check_result(result)
        return result['data'][0]['ordId']


    @retry_on_exception(logger)
    def change_stoploss_order(self, price:float, orderId:str) -> None:
        result = self.tradeAPI.amend_algo_order(
            instId=self.instId, algoId=orderId, newSlTriggerPx=str(price)
        )
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def construct_takeprofit_order(self) -> str:
        side = self.__check_pos_side()
        result = self.tradeAPI.place_algo_order(
            instId=self.instId, tdMode=self.mgnMode, side=side,
            posSide=self.posSide, ordType='conditional', sz=self.size,
            tpTriggerPx=self.tpPrice, tpOrdPx='-1', tpTriggerPxType='last'
        )
        self.__check_result(result)
        return result['data'][0]['ordId']


    @retry_on_exception(logger)
    def change_takeprofit_order(self, tpPrice:float, orderId:str):
        result = self.tradeAPI.amend_algo_order(
            instId=self.instId, algoId=orderId, newTpTriggerPx=str(tpPrice)
        )
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def costruct_limit_order(self, price) -> dict:
        side = self.__check_pos_side()
        result = self.tradeAPI.place_order(
            instId=self.instId, tdMode=self.mgnMode, side=side,
            posSide=self.posSide, ordType='limit', px=price,
            sz=str(self.size)
        )
        self.__check_result(result)
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    @retry_on_exception(logger)
    def calculate_posSize(self) -> float:
        return ((OKXInfoFunctions().check_balance()) * self.leverage * self.risk) / self.slPrice


    def check_position(self, ordId) -> dict:
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        self.__check_result(result)
        return float(result["data"][0]["avgPx"])


    @retry_on_exception(logger)
    def get_all_order_list(self) -> dict:
        result = self.tradeAPI.get_order_list()
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def get_all_opened_positions(self) -> dict:
        result = self.accountApi.get_positions()
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def get_history(self) -> dict:
        result = self.tradeAPI.get_fills(instType = 'SWAP') #скорее всего всегда SWAP
        self.__check_result(result)
        return result