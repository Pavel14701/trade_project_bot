from datetime import datetime, timedelta
import okx.Account as Account
import okx.Trade as Trade
from datasets.database import TradeUserData
from datasets.database import Session
from UserInfoFunctions import UserInfo


# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'


class PlaceOrders:
    def __init__(
            self, passphrase, secret_key, api_key,
            tradeAction, flag, instId=None, size=None, posSide=None,
            leverage=None, risk=None, tpPrice=None, slPrice=None, mgnMode=None
            ):
        self.passphrase = passphrase
        self.secret_key = secret_key
        self.api_key = api_key
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
        self.leverage = leverage
        self.accountApi = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
 
        self.leverage = UserInfo.set_leverage_inst(api_key, secret_key, 
                                                   passphrase, False, flag, 
                                                   instId, leverage, mgnMode)

        
    # Создание маркет ордера long с Tp и Sl
    def place_market_order(self):
        # установка левериджа
        result = self.leverage
        usdt_balance = UserInfo.check_balance(self.api_key, self.secret_key, self.passphrase, self.flag)
        # Создаём ордер лонг по маркету
        result = self.tradeAPI.place_order(
            instId=self.instId,
            tdMode=self.mgnMode,
            side=self.tradeAction,
            posSide=self.posSide,
            ordType="market",
            sz=self.size
        )
        if result["code"] == "0":
            print("Successful order request,order_id = ",result["data"][0]["ordId"])
            order_id_market = result["data"][0]["ordId"]
            result_enter_price = self.tradeAPI.get_order(instId="BTC-USDT-SWAP", ordId="676182969496752129")
            enter_price = float(result["data"][0]["avgPx"])
            # Создаем ордер tp
            if self.tradeAction == 'buy':
                tpslTradeAction = 'sell'
            elif self.tradeAction == 'sell':
                tpslTradeAction = 'buy'
            result_tp = self.tradeAPI.place_algo_order(
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
            result_sl = self.tradeAPI.place_algo_order(
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
            print("Unsuccessful order request, error_code = ",result["data"][0]["test.log"], ", Error_message = ", result["data"][0]["sMsg"])


    # Размещение лимитного ордера
    def place_limit_order(self, price):
        # Установка левериджа
        result = self.leverage
        # Баланс
        balance = self.balance
        # limit order
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
            order_id_limit = result["data"][0]["ordId"]
            # Нужно встроить логику нахождения стопа и сохранять его в бд
            with Session() as session:
                order_id = TradeUserData(
                order_id=order_id_limit,
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


    #Калькулятор стопа
    @staticmethod 
    def calculate_pos_size(leverage, instId, volat, enter_price, balance, direction, timeframe):
        print(volat)
        risk = 0.03
        if direction == "long":
            # Рассчитываем стоп-лос
            slPrice = enter_price - (enter_price * volat[f'{instId}_{timeframe}'] / leverage)
        elif direction == "short":
            # Рассчитываем стоп-лос
            slPrice = enter_price + (enter_price * volat[f'{instId}_{timeframe}'] / leverage)
        # Рассчитываем размер позиции
        P = (balance * leverage * risk) / slPrice
        #   Выводим результаты
        print(f"Стоп-лос: {slPrice:.2f}")
        print(f"Размер позиции: {P:.2f}")
        return slPrice


    # Открытые ордера
    @staticmethod
    def get_all_order_list(self):
        result = self.tradeAPI.get_order_list()
        print(result)
        return result


    # Открытые позиции
    @staticmethod
    def get_all_opened_positions(self):
        result = self.accountAPI.get_positions()
        print(result)
        return result


    # История торгов за три дня
    @staticmethod
    def get_history_3days(self, instType):
        result = self.tradeAPI.get_fills(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result


    # История торгов за 3 месяца
    @staticmethod
    def get_history_3months(self, instType):
        result = self.tradeAPI.get_fills_history(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result

    
    # Просмотр инфы по позиции через её id
    @staticmethod
    def check_position(self, ordId):
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        print(result)
        enter_price = float(result["data"][0]["avgPx"])
        print(enter_price)
        return result

