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
    """Summary:
    Class for placing orders, managing positions, and retrieving trade history.

    Explanation:
    This class provides methods for placing market and limit orders, calculating position size and stop loss, retrieving open orders, open positions, trade history, and checking position information.

    Returns:
    - For place_market_order,
    - For place_limit_order,
    - For calculate_pos_size,
    - For get_all_order_list,
    - For get_all_opened_positions,
    - For get_history_3days,
    - For get_history_3months,
    - For check_position: None
    """
    
    
    def __init__(
            self, passphrase, secret_key, api_key,
            tradeAction, flag, instId=None, size=None, posSide=None,
            leverage=None, risk=None, tpPrice=None, slPrice=None, mgnMode=None
            ):
        """Summary:
        Initialize trade parameters for placing orders.

        Explanation:
        This function initializes the trade parameters including passphrase, secret key, API key, trade action, flag, instrument ID, order size, position side, leverage, risk, take profit price, stop loss price, and margin mode for executing trades.

        Args:
        - passphrase: The passphrase for API authentication.
        - secret_key: The secret key for API authentication.
        - api_key: The API key for API authentication.
        - tradeAction: The type of trade action (buy or sell).
        - flag: A flag indicating a specific condition or setting.
        - instId: The instrument ID for the trade.
        - size: The size or quantity of the order.
        - posSide: The position side (long or short).
        - leverage: The leverage amount for the trade.
        - risk: The risk factor for the trade.
        - tpPrice: The take profit price for the trade.
        - slPrice: The stop loss price for the trade.
        - mgnMode: The margin mode for the trade.

        Returns:
        None
        """
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
        """Summary:
        Place a market order with take profit and stop loss.

        Explanation:
        This function places a market order with specified parameters such as instrument ID, margin mode, trade action, position side, order size, take profit price, and stop loss price. It also creates take profit and stop loss orders based on the market order execution.

        Returns:
        None
        """
        # sourcery skip: extract-method, switch
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
        """Summary:
        Place a limit order with specified price.

        Explanation:
        This function places a limit order with the given price for the instrument, margin mode, trade action, position side, order size, and leverage. It also handles the result of the order placement and stores relevant information in the database.

        Args:
        - price: The price at which the limit order will be placed.

        Returns:
        None
        """
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
        """Summary:
        Calculate position size and stop loss price.

        Explanation:
        This static method calculates the stop loss price and position size based on the provided leverage, instrument ID, volatility, entry price, balance, trade direction, and timeframe.

        Args:
        - leverage: The leverage amount for the trade.
        - instId: The instrument ID for the trade.
        - volat:  Index volatility data.
        - enter_price: The entry price for the trade.
        - balance: The balance available for trading.
        - direction: The direction of the trade (long or short).
        - timeframe: The timeframe for the trade.

        Returns:
        - The calculated stop loss price.
        """
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
        """Summary:
        Retrieve a list of all open orders.

        Explanation:
        This static method retrieves and prints a list of all open orders using the trade API.

        Returns:
        - The list of all open orders.
        """
        result = self.tradeAPI.get_order_list()
        print(result)
        return result


    # Открытые позиции
    @staticmethod
    def get_all_opened_positions(self):
        """Summary:
        Retrieve a list of all opened positions.

        Explanation:
        This static method fetches and prints a list of all opened positions using the account API.

        Returns:
        - The list of all opened positions.
        """
        result = self.accountAPI.get_positions()
        print(result)
        return result


    # История торгов за три дня
    @staticmethod
    def get_history_3days(self, instType):
        """Summary:
        Retrieve trade history for the last three days.

        Explanation:
        This static method retrieves and prints the trade history for the last three days based on the specified instrument type, typically SWAP.

        Args:
        - instType: The instrument type for which the trade history is requested.

        Returns:
        - The trade history data for the last three days.
        """
        result = self.tradeAPI.get_fills(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result


    # История торгов за 3 месяца
    @staticmethod
    def get_history_3months(self, instType):
        """Summary:
        Retrieve trade history for the last three months.

        Explanation:
        This static method fetches and prints the trade history for the last three months based on the specified instrument type, typically SWAP.

        Args:
        - instType: The instrument type for which the trade history is requested.

        Returns:
        - The trade history data for the last three months.
        """
        result = self.tradeAPI.get_fills_history(
            instType = instType #скорее всего всегда SWAP
        )
        print(result)
        return result

    
    # Просмотр инфы по позиции через её id
    @staticmethod
    def check_position(self, ordId):
        """Summary:
        Check position information by order ID.

        Explanation:
        This static method retrieves and prints information about a position based on the provided order ID.

        Args:
        - ordId: The order ID for which position information is requested.

        Returns:
        - The position information for the specified order ID.
        """
        result = self.tradeAPI.get_order(instId=self.instId, ordId=ordId)
        print(result)
        enter_price = float(result["data"][0]["avgPx"])
        print(enter_price)
        return result

