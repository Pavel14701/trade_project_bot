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


    def construct_market_order(self, side):  
        # sourcery skip: class-extract-method
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=side,
            posSide=side,
            ordType="market",
            sz=self.size
        )
        if result["code"] == "0":
            print("Successful order request,order_id = ",result["data"][0]["ordId"])
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return result, order_id, outTime



    def construct_stoploss_order(self, side):
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
        if result['code'] == '0':
            print("Successful order request,order_id = ",result["data"][0]["ordId"])
            return result['data'][0]['ordId']
        
        
    def construct_takeprofit_order(self, side):
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
        if result['code'] == '0':
            print("Successful order request,order_id = ",result["data"][0]["ordId"])
            return result['data'][0]['ordId']


    def costruct_limit_order(self, price):
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=self.tradeAction,
            posSide=self.posSide,
            ordType="limit",
            px=price,
            sz=self.size
        )
        print(result)
        if result["code"] == "0":
            print("Successful order request, order_id = ",result["data"][0]["ordId"])
        outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        order_id = result["data"][0]["ordId"]
        return result, order_id, outTime


    def calculate_posSize(self):
        # sourcery skip: inline-immediately-returned-variable
        user = UserInfo()
        balance = user.check_balance()
        size = (balance * self.leverage * self.risk) / self.slPrice
        return size
    
    def check_position(self, ordId):
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        print(result)
        with contextlib.suppress(Exception):
            enter_price = float(result["data"][0]["avgPx"])
        print(enter_price)
        return result
    
    
    # Открытые ордера
    def get_all_order_list(self):
        result = self.tradeAPI.get_order_list()
        print(result)
        return result


    # Открытые позиции
    def get_all_opened_positions(self):
        result = self.accountAPI.get_positions()
        print(result)
        return result


    # История торгов за три дня
    def get_history_3days(self, instType):
        result = self.tradeAPI.get_fills(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result


    # История торгов за 3 месяца
    def get_history_3months(self, instType):
        result = self.tradeAPI.get_fills_history(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result