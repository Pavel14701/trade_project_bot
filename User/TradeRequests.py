import contextlib
from datetime import datetime, timedelta
import okx.Account as Account
import okx.Trade as Trade
from User.LoadSettings import LoadUserSettingData
from User.UserInfoFunctions import UserInfo


class OKXTradeRequests(LoadUserSettingData):
    def __init__(
            self,
            instId=None|str, size=None|float, posSide=None|str, tpPrice=None|float,
            slPrice=None|float
            ):
        super().__init__()
        self.instId = instId
        self.size = size
        self.posSide = posSide #long or short
        self.tpPrice = tpPrice
        self.slPrice = slPrice
        self.accountApi = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.tradeAPI = Trade.TradeAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)


    def construct_market_order(self, side) -> dict:
        if self.posSide == 'long':
                    side = 'buy'
        elif self.posSide == 'short':
                    side = 'sell'
        # sourcery skip: class-extract-method
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=side,
            ordType="market",
            sz=self.size
        )
        if result['code'] != '0':
            raise ValueError(f'Construct market order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}



    def construct_stoploss_order(self) -> str:
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
            slTriggerPx=self.slPrice,
            slOrdPx="-1",
            slTriggerPxType="last"
        )
        if result['code'] != '0':
            raise ValueError(f'Construct stoploss order, code: {result['code']}')
        return result['data'][0]['ordId']
        
        
    def construct_takeprofit_order(self, side) -> str:
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


    def costruct_limit_order(self, price) -> dict:
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
            sz=self.size
        )
        if result["code"] != "0":
            raise ValueError(f'Construct limit order, code: {result['code']}')
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return {'result': result, 'order_id': order_id, 'outTime': outTime}


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

    
    
    # Открытые ордера
    def get_all_order_list(self) -> dict:
        return self.tradeAPI.get_order_list()


    # Открытые позиции
    def get_all_opened_positions(self) -> dict:
        return self.accountAPI.get_positions()


    # История торгов за три дня
    def get_history_3days(self) -> dict:
        return self.tradeAPI.get_fills(instType = 'SWAP') #скорее всего всегда SWAP


    # История торгов за 3 месяца
    def get_history_3months(self) -> dict:
        return self.tradeAPI.get_fills_history(instType = 'SWAP') #скорее всего всегда SWAP