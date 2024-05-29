import os
from datetime import datetime, timedelta
import okx.Account as Account
import okx.Trade as Trade
from database import TradeUserData
from database import Session

# Данные Api
passphrase = os.getenv("PASSPHRASE")
secret_key = os.getenv("SECRET_KEY")
api_key = os.getenv("API_KEY")
# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
# Формируем объект tradeApi
flag = "1"  # live trading: 0, demo trading: 1
instType = 'SWAP'
leverage = 10
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

class PlaceOrders:
    def __init__(self, tradeAction, flag, instId, size, posSide, levarage, risk, tpPrice, slPrice, mgnMode):
        self.flag = flag
        self.instId = instId
        self.size = size
        self.posSide = posSide #long or short
        self.leverage = leverage
        self.risk = risk
        self.tpPrice = tpPrice
        self.slPrice = slPrice
        self.mgnMode = mgnMode # cross or isolated
        self.tradeAction = tradeAction # buy or sell
        
    # Создание маркет ордера long с Tp и Sl
    def place_market_order(self, accountAPI, tradeAPI):
        # установка левериджа
        result = accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            mgnMode = self.mgnMode
        )
        # Баланс
        result_bal = accountAPI.get_account_balance()
        usdt_balance = float(result_bal["data"][0]["details"][0]["availBal"]) # получаем значение ключа ccy по указанному пути
        usdt_balance = int(usdt_balance)
        # Создаём ордер лонг по маркету
        result = tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=self.tradeAction,
            posSide=self.posSide,
            ordType="market",
            sz=self.size
        )
        if result["code"] == "0":
            print("Successful order request，order_id = ",result["data"][0]["ordId"])
            order_id_market = result["data"][0]["ordId"]
            result_enter_price = tradeAPI.get_order(instId="BTC-USDT-SWAP", ordId="676182969496752129")
            enter_price = float(result["data"][0]["avgPx"])
            # Создаем ордер tp
            if self.tradeAction == 'buy':
                tpslTradeAction = 'sell'
            elif self.tradeAction == 'sell':
                tpslTradeAction = 'buy'
            result_tp = tradeAPI.place_algo_order(
                instId=self.instId,
                tdMode=self.mgnMode,
                side=tpslTradeAction,
                posSide=self.posSide,
                ordType="conditional",
                sz=self.size,
                tpTriggerPx=self.tpPrice,
                tpOrdPx="-1",
                tpTriggerPxType="last"
            )
            order_id_tp_market = result_tp["data"][0]["algoId"]
            # Создаём ордер sl
            result_sl = tradeAPI.place_algo_order(
                instId=self.instId,
                tdMode=self.mgnMode,
                side=tpslTradeAction,
                posSide=self.posSide,
                ordType="conditional",
                sz=self.size,
                slTriggerPx=self.slPrice,
                slOrdPx="-1",
                slTriggerPxType="last"
            )
            order_id_sl_market = result_sl["data"][0]["algoId"]
            outTime = datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
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
            print("Unsuccessful order request，error_code = ",result["data"][0]["test.log"], ", Error_message = ", result["data"][0]["sMsg"])

    # Размещение лимитного ордера
    def place_limit_order(self, price):
        # Установка левериджа
        result = accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            mgnMode = self.mgnMode
        )
        # Баланс
        result_bal = accountAPI.get_account_balance()
        usdt_balance = float(result_bal["data"][0]["details"][0]["availBal"]) # получаем значение ключа ccy по указанному пути
        usdt_balance = int(usdt_balance)
        # limit order
        result = tradeAPI.place_order(
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
            order_id_limit = result["data"][0]["ordId"]
            # Нужно встроить логику нахождения стопа и сохранять его в бд
            with Session() as session:
                order_id = TradeUserData(
                order_id=order_id_limit,
                status=False,
                order_volume=self.size,
                balance=usdt_balance,
                instrument=self.instId,
                leverage=self.leverage,
                time=outTime,
                side_of_trade=self.posSide
                )    
        else:
            print("Unsuccessful order request，error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])
        
  # Открытые ордера
    def get_all_order_list():
        result = tradeAPI.get_order_list()
        print(result)

    # Открытые позиции
    def get_all_opened_positions():
        result = accountAPI.get_positions()
        print(result)

    # История торгов за три дня
    def get_history_3days(insType):
        result = tradeAPI.get_fills(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)

    # История торгов за 3 месяца
    def get_history_3months(instType):
        result = tradeAPI.get_fills_history(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        
    def check_position(self, ordId):
        result = tradeAPI.get_order(instId=self.instId, ordId=ordId)
        print(result)
        enter_price = float(result["data"][0]["avgPx"])
        print(enter_price)

