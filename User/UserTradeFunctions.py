import contextlib
from datetime import datetime, timedelta
import okx.Account as Account
import okx.Trade as Trade
from datasets.database import DataAllDatasets, Base
from datasets.database import Session
from User.UserInfoFunctions import UserInfo
from User.LoadSettings import LoadUserSettingData
from User.TradeRequests import OKXTradeRequests


# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'
bd = DataAllDatasets(Session)
TradeUserData = bd.create_TradeUserData(Base)

class PlaceOrders(LoadUserSettingData, OKXTradeRequests):    
    def __init__(
            self, tradeAction: str,
            instId=None|str, size=None|float, posSide=None|str, tpPrice=None|float,
            slPrice=None|float
            ):
        super().__init__(tradeAction, instId, size, posSide, tpPrice, slPrice)
        self.leverage = self.UserInfo.set_leverage_inst(self.instId, self.leverage, self.mgnMode)

        
    # Создание маркет ордера long с Tp и Sl
    def place_market_order(self):
        # sourcery skip: extract-method, switch
        if self.tradeAction == 'buy':
                tpslTradeAction = 'sell'
        elif self.tradeAction == 'sell':
                tpslTradeAction = 'buy'
        # установка левериджа
        result = self.leverage
        usdt_balance = self.UserInfo.check_balance()
        # Создаём ордер лонг по маркету
        order_id_market, outTime = super().construct_market_order()
        if order_id_market is not None:
            # Получаем точку входа
            enter_price = float((super().check_position(order_id_market))["data"][0]["avgPx"])
            if self.tpPrice is None:
                order_id_tp_market = None
            else:
                order_id_tp_market = super().construct_takeprofit_order(tpslTradeAction)
            # Создаём ордер sl
            order_id_sl_market = super().construct_stoploss_order(tpslTradeAction)
            with Session() as session:
                order_id = TradeUserData(
                    order_id=order_id_market,
                    status=True, # Статус указывает выполнен ордер или нет
                    order_volume=self.size,
                    tp_order_volume=self.size,
                    sl_order_volume=self.size,
                    balance=usdt_balance,
                    instrument=self.instId,
                    leverage=self.leverage,
                    side_of_trade=self.posSide,
                    enter_price=enter_price,
                    time=outTime,
                    tp_order_id=order_id_tp_market,
                    tp_price=self.tpPrice,
                    sl_order_id=order_id_sl_market,
                    sl_price=self.slPrice
                )
                session.add(order_id)
                session.commit()
        else:
            print("Unsuccessful order request, error_code = ",result["data"][0], ", Error_message = ", result["data"][0]["sMsg"])
        
        
    # Размещение лимитного ордера
    def place_limit_order(self, price):
        # Установка левериджа
        result = self.leverage
        # Баланс
        balance = self.balance
        # limit order
        order_id, outTime = super().construct_limit_order(price)
        if order_id is not None:
            with Session() as session:
                order_id = TradeUserData(
                order_id=order_id,
                status=False,
                order_volume=self.size,
                balance=balance,
                instrument=self.instId,
                leverage=self.leverage,
                time=outTime,
                side_of_trade=self.posSide
                )
                session.add(order_id)
                session.commit    
        else:
            print("Unsuccessful order request，error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])




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

    
    # Просмотр инфы по позиции через её id
    def check_position(self, ordId):
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        print(result)
        with contextlib.suppress(Exception):
            enter_price = float(result["data"][0]["avgPx"])
        print(enter_price)
        return result

