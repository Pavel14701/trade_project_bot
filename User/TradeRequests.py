
from datetime import datetime, timedelta
import okx.Account as Account
import okx.Trade as Trade
from User.LoadSettings import LoadUserSettingData
from User.UserInfoFunctions import UserInfo
from utils.CustomDecorators import retry_on_exception

retry_settings = LoadUserSettingData.load_retry_requests_configs()
max_retries = retry_settings['max_retries']
delay = retry_settings['delay']


class OKXTradeRequests:
    def __init__(
            self,
            instId=None|str, size=None|float, posSide=None|str, tpPrice=None|float,
            slPrice=None|float
            ):
        api_settings = LoadUserSettingData.load_api_setings()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        self.instId = instId
        self.size = size
        user_settings = LoadUserSettingData.load_user_settings()
        self.mgnMode = user_settings['mgnMode']
        self.leverage = user_settings['leverage']
        self.risk = user_settings['risk']
        self.posSide = posSide #long or short
        self.tpPrice = tpPrice
        self.slPrice = slPrice


    def create_account_api(self):
        self.accountApi = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    def create_trade_api(self):
        self.tradeAPI = Trade.TradeAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    @retry_on_exception(max_retries, delay)
    def construct_market_order(self, side) -> dict:
        self.create_trade_api()
        if self.posSide == 'long':
                    side = 'buy'
        elif self.posSide == 'short':
                    side = 'sell'
        # sourcery skip: class-extract-method
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="market",
            sz=str(self.size)
        )
        if result['code'] != '0':
            raise ValueError(f'Construct market order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}



    @retry_on_exception(max_retries, delay)
    def construct_stoploss_order(self) -> str:
        self.create_trade_api()
        if self.posSide == 'long':
                    side = 'sell'
        elif self.posSide == 'short':
                    side = 'buy'
        result = self.tradeAPI.place_algo_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="conditional",
            sz=str(self.size),
            slTriggerPx=str(self.slPrice),
            slOrdPx="-1",
            slTriggerPxType="last"
        )
        if result['code'] != '0':
            raise ValueError(f'Construct stoploss order, code: {result['code']}')
        return result['data'][0]['ordId']
    
    
    @retry_on_exception(max_retries, delay)
    def change_stoploss_order(self, price:float, orderId:str) -> None:
        self.create_trade_api()
        result = self.tradeAPI.amend_algo_order(
            instId=self.instId,
            algoId=orderId,
            newSlTriggerPx=str(price)
        )
        if result['code'] != '0':
            raise ValueError(f'Change stoploss order, code: {result['code']}')
        
        
    @retry_on_exception(max_retries, delay)
    def construct_takeprofit_order(self, side) -> str:
        self.create_trade_api()
        if self.posSide == 'long':
                    side = 'sell'
        elif self.posSide == 'short':
                    side = 'buy'
        result = self.tradeAPI.place_algo_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="conditional",
            sz=self.size,
            tpTriggerPx=self.tpPrice,
            tpOrdPx="-1",
            tpTriggerPxType="last"
        )
        if result['code'] != '0':
            raise ValueError(f'Construct takeprofit order, code: {result['code']}')
        return result['data'][0]['ordId']
    
    
    @retry_on_exception(max_retries, delay)
    def change_takeprofit_order(self, tpPrice:float, orderId:str):
        self.create_trade_api()
        result = self.tradeAPI.amend_algo_order(
            instId=self.instId,
            algoId=orderId,
            newTpTriggerPx=str(tpPrice)
        )
        if result['code'] != '0':
            raise ValueError(f'Change stoploss order, code: {result['code']}')


    @retry_on_exception(max_retries, delay)
    def costruct_limit_order(self, price) -> dict:
        self.create_trade_api()
        if self.posSide == 'long':
                    side = 'buy'
        elif self.posSide == 'short':
                    side = 'sell'
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="limit",
            px=price,
            sz=str(self.size)
        )
        if result["code"] != "0":
            raise ValueError(f'Construct limit order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


    @retry_on_exception(max_retries, delay)
    def calculate_posSize(self) -> float:
        # sourcery skip: inline-immediately-returned-variable
        user = UserInfo()
        balance = user.check_balance()
        return (balance * self.leverage * self.risk) / self.slPrice


    def check_position(self, ordId) -> dict:
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        if result["code"] != "0":
            raise ValueError(f'Check position, code: {result['code']}')
        return float(result["data"][0]["avgPx"])


    @retry_on_exception(max_retries, delay)
    def get_all_order_list(self) -> dict:
        result = self.tradeAPI.get_order_list()
        if result["code"] != "0":
            raise ValueError(f'Get all order list, code: {result['code']}')


    @retry_on_exception(max_retries, delay)
    def get_all_opened_positions(self) -> dict:
        result = self.accountApi.get_positions()
        if result["code"] != "0":
            raise ValueError(f'Get all opened positions, code: {result['code']}')


    @retry_on_exception(max_retries, delay)
    def get_history(self) -> dict:
        result = self.tradeAPI.get_fills(instType = 'SWAP') #скорее всего всегда SWAP
        if result["code"] != "0":
            raise ValueError(f'Get history, code: {result['code']}')

