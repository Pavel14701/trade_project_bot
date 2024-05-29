
# Импорт либ
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import okx.Account as Account
import okx.Trade as Trade
import okx.TradingData as TradingData
import okx.Funding as Funding
# на потом
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

# Данные Api
passphrase = os.getenv("PASSPHRASE")
secret_key = os.getenv("SECRET_KEY")
api_key = os.getenv("API_KEY")
# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
# Формируем объект tradeApi
flag = "1"  # live trading: 0, demo trading: 1
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)


# создаем движок для подключения к базе данных
engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserData.db")
# создаем базовый класс для декларативных классов
Base = declarative_base()
# определяем класс, который представляет таблицу
class TradeUserData(Base):
    __tablename__ = "positions_and_orders"
    order_id = Column(String, primary_key=True)
    balance = Column(Integer)
    instrument = Column(String)
    enter_price = Column(Numeric(10, 4))
    price_of_1contr = Column(Numeric(10, 4))
    number_of_contracts = Column(Numeric(10, 4))
    money_in_deal = Column(Integer)
    side_of_trade = Column(String)
    order_volume = Column(Integer)
    leverage = Column(Integer)
    time = Column(DateTime)
    status = Column(Boolean)
    tp_price = Column(Numeric(10, 4))
    tp_order_id = Column(String)
    tp_order_volume = Column(Integer)
    sl_price = Column(Numeric(10, 4))
    sl_order_id = Column(String)
    sl_order_volume = Column(Integer)
    risk_coef = Column(Numeric(10, 4))
    close_price = Column(Numeric(10, 4))
    money_income = Column(Integer)
    percent_money_income = Column(Numeric(10, 4))
# создаем таблицу в базе данных, если она еще не существует
Base.metadata.create_all(engine)
# создаем фабрику сессий
Session = sessionmaker(bind=engine)
# создаем сессию
session = Session()
session.close()




# Создаём функции для проверки информации
# Проверка баланса
def check_balance():
  flag = "1"  # live trading: 0, demo trading: 1
  accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
  result_bal = accountAPI.get_account_balance()
  usdt_balance = Decimal(result_bal["data"][0]["details"][0]["availBal"]) # получаем значение ключа ccy по указанному пути
  usdt_balance = int(usdt_balance)
  print (usdt_balance) # выводим значение на экран
  print(f'Баланс: \n {result_bal}\n\n')

# Фандинг  В демо не доступен
def fanding():
  flag = "1"  # live trading:0 , demo trading：1
  fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
  result = fundingAPI.get_currencies()
  print(f'Фандинг: \n {result} \n\n')

# Конфигурация режима маржи
def account_config():
  flag = "1"  # live trading: 0, demo trading: 1
  result = accountAPI.get_account_config()
  print(f'Конфигурации режима маржи: \n {result}')
  if result['code'] == "0":
      acctLv = result["data"][0]["acctLv"]
      if acctLv == "1":
          print("Simple mode\n\n")
      elif acctLv == "2":
          print("Single-currency margin mode\n\n")
      elif acctLv == "3":
          print("Multi-currency margin mode\n\n")
      elif acctLv == "4":
          print("Portfolio margin mode\n\n")

# Поиск(пока нет) доступных инструментов
def get_public_data():
  flag = "1"  # live trading: 0, demo trading: 1
  publicDataAPI = PublicData.PublicAPI(flag = flag)
  result = publicDataAPI.get_instruments(instType = "SWAP")
  print(f'Доступные инструменты: \n{result}\n\n')



# \---! Все эти функции можно всунуть в одну и передавать в них аргументы !---/ #
# установить леверидж для кросса
def set_leverage_cross():
  # Set leverage to be 5x for all cross-margin BTC-USDT SWAP positions,
  # by providing any SWAP instId with BTC-USDT as the underlying
  instId = "BTC-USDT-SWAP"
  result = accountAPI.set_leverage(
      instId = instId,
      lever = "13",
      mgnMode = "cross"
  )
  print(f'Установка левириджа, кросс для {instId}: \n{result}\n\n')

# установить леверидж для всех типов изолированных ордеров(лонг, шорт)
def set_leverage_isolated():
  # Set leverage to be 5x for all isolated-margin BTC-USDT SWAP positions,
  # by providing any SWAP instId with BTC-USDT as the underlying
  instId = "BTC-USDT-SWAP"
  result = accountAPI.set_leverage(
      instId = instId,
      lever = "5",
      mgnMode = "isolated"
  )
  print(f'Установка левириджа для всех типов изолированых позиций {instId}:\n {result}\n\n')

# Установка левериджа для изолированных позиций типа long
def set_leverage_isolated_long():
  # Set leverage to be 5x for an isolated-margin
  # BTC-USDT-SWAP long position;
  # This does NOT affect the leverage of any other BTC-USDT SWAP positions with different maturities or posSide
  instId = "BTC-USDT-SWAP"
  result = accountAPI.set_leverage(
      instId = instId,
      lever = "5",
      posSide = "long",
      mgnMode = "isolated"
  )
  print(f'Установка левериджа для изолированных лонг {instId}: \n{result}\n\n')

# Установка левериджа для изолированных позиций типа short
def set_leverage_isolated_short():
  # Set leverage to be 5x for an isolated-margin
  # BTC-USDT-SWAP long position;
  # This does NOT affect the leverage of any other BTC-USDT SWAP positions with different maturities or posSide
  instId = "BTC-USDT-SWAP"
  result = accountAPI.set_leverage(
      instId = instId,
      lever = "5",
      posSide = "short",
      mgnMode = "isolated"
  )
  print(f'Установка левериджа для short позиций {instId}: \n{result}\n\n')
#\---! --- !---/#


# Установка режима торговли
def set_trading_mode():
  result = accountAPI.set_position_mode(
      posMode="long_short_mode"
  )
  print(result)



#стоп ордер для лимита лонг
def stop_for_limit_long():
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="sell",
      posSide="long",
      ordType="trigger",
      sz="1",
      triggerPx="50000",
      tpTriggerPx="50000",
      slTriggerPx="40000",
      tpOrdPx="49900",
      slOrdPx="40100"
  )
  print(result)

#стоп ордер для лимита шорт
def stop_for_limit_short():
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="buy",
      posSide="short",
      ordType="trigger",
      sz="1",
      triggerPx="50000",
      tpTriggerPx="50000",
      slTriggerPx="40000",
      tpOrdPx="49900",
      slOrdPx="40100"
  )
  print(result)

# Создание лимитных ордеров
# Важный нюанс касательно лимитов, нельзя выставлять ордера лонг выше цены маркировки и нельзя выставлять ордера ниже цены маркировки, это защита от мнимых сделок
# Создание лимитного ордера long(кросс-маржа)
def place_long_limit_order(price):
  # limit order
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="buy",
      posSide="long",
      ordType="limit",
      px=price,
      sz="100"
  )
  print(result)

  if result["code"] == "0":
      print("Successful order request，order_id = ",result["data"][0]["ordId"])
      order_id_limit_long = result["data"][0]["ordId"]
      return order_id_limit_long
      result = tradeAPI.place_order(      instId="BTC-USDT-SWAP",
          tdMode="cross",
          side="sell",
          posSide="long",
          ordType="trigger",
          sz="1",
          triggerPx="50000",
          tpTriggerPx="50000",
          slTriggerPx="40000",
          tpOrdPx="49900",
          slOrdPx="40100"
      )
      print(result)
      sltp_long_order_id = result["data"][0]["ordId"]
      return sltp_long_order_id
  else:
      print("Unsuccessful order request，error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])


# Размещение лимитного ордера шорт
def place_short_limit_order(price):
  # limit order
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="sell",
      posSide="short",
      ordType="limit",
      px=price,
      sz="50"
  )
  print(result)

  if result["code"] == "0":
      print("Successful order request，order_id = ",result["data"][0]["ordId"])
      order_id_limit_short = result["data"][0]["ordId"]
      stop_for_limit_short()
      return order_id_limit_short

  else:
      print("Unsuccessful order request，error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])


instId = "BTC-USDT-SWAP"
size = 100
tpPrice = 54000
slPrice = 44000
leverage = 10
posSide = "long"
risk = 0.03
# Маркет ордера
# Создание маркет ордера long с Tp и Sl
def place_market_long_order(instId, leverage, size, tpPrice, slPrice, accountAPI, posSide):
  # Создаём переменные локально
  instId = instId
  size = size
  tpPrice = tpPrice
  slPrice = slPrice
  leverage = leverage
  posSide = posSide
  flag = "1"  # live trading: 0, demo trading: 1
  # Леверидж
  result = accountAPI.set_leverage(
      instId = instId,
      lever = leverage,
      mgnMode = "cross"
  )
  # Баланс
  result_bal = accountAPI.get_account_balance()
  usdt_balance = float(result_bal["data"][0]["details"][0]["availBal"]) # получаем значение ключа ccy по указанному пути
  usdt_balance = int(usdt_balance)
  print (usdt_balance) # выводим значение на экран
  print(f'Баланс: \n {result_bal}\n\n')
  # Создаём ордер лонг по маркету
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="buy",
      posSide=posSide,
      ordType="market",
      sz=size
  )
  print(result)
  if result["code"] == "0":
      print("Successful order request，order_id = ",result["data"][0]["ordId"])
      order_id_market_long = result["data"][0]["ordId"]
      order_id = TradeUserData(order_id=order_id_market_long)
      result_enter_price = tradeAPI.get_order(instId="BTC-USDT-SWAP", ordId="676182969496752129")
      print(result_enter_price)
      enter_price = float(result["data"][0]["avgPx"])
      print(enter_price)
      # Добавляем объект в сессию
      session.add(order_id)
      # Сохраняем изменения в базе данных
      session.commit()
      # Настраиваем фильтр по primarykey(order_id)
      order_id_main = session.query(TradeUserData).filter_by(order_id=order_id_market_long).first()
      # Вносим Объекты в бд
      order_id_main.status = True
      order_id_main.order_volume = size
      order_id_main.tp_order_volume = size
      order_id_main.sl_order_volume = size
      order_id_main.balance = usdt_balance
      order_id_main.instrument = instId
      order_id_main.leverage = leverage
      order_id_main.side_of_trade = "long"
      order_id_main.enter_price = enter_price
      session.commit()
      # Создаем ордер tp
      result_tp = tradeAPI.place_algo_order(
          instId="BTC-USDT-SWAP",
          tdMode="cross",
          side="sell",
          posSide="long",
          ordType="conditional",
          sz=size,
          tpTriggerPx=tpPrice,
          tpOrdPx="-1",
          tpTriggerPxType="last"
      )
      print(result_tp)
      order_id_tp_market_long = result_tp["data"][0]["algoId"]
      order_id_main.tp_order_id = order_id_tp_market_long
      order_id_main.tp_price = tpPrice
      session.commit()
      result_sl = tradeAPI.place_algo_order(
          instId="BTC-USDT-SWAP",
          tdMode="cross",
          side="sell",
          posSide="long",
          ordType="conditional",
          sz=size,
          slTriggerPx=slPrice,
          slOrdPx="-1",
          slTriggerPxType="last"
      )
      print(result_sl)
      order_id_sl_market_long = result_sl["data"][0]["algoId"]
      order_id_main.sl_order_id = order_id_sl_market_long
      order_id_main.sl_price = slPrice
      session.commit()
      # Преобразуем милисекунды в секунды и дату и время
      outTime = int(result['outTime'])
      outTime = outTime / 1000000
      outTime = datetime.fromtimestamp(outTime)
      outTime = outTime + timedelta(hours=3)
      print('time: ', outTime)
      order_id_main.time = outTime
      session.commit()
      # Кроем сессию
      session.close()
  else:
      print("Unsuccessful order request，error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])



# Создание маркет ордера short с sl и тп
def place_market_short_order(size, tpPrice, slPrice):
  result = tradeAPI.place_order(
      instId="BTC-USDT-SWAP",
      tdMode="cross",
      side="sell",
      posSide="short",
      ordType="market",
      sz=size
  )
  print(result)

  if result["code"] == "0":
      print("Successful order request，order_id = ",result["data"][0]["ordId"])
      order_id_market_short = result["data"][0]["ordId"]
      result_tp = tradeAPI.place_algo_order(
          instId="BTC-USDT-SWAP",
          tdMode="cross",
          side="buy",
          posSide="short",
          ordType="conditional",
          sz=size,
          tpTriggerPx=tpPrice,
          tpOrdPx="-1",
          tpTriggerPxType="last"
      )
      print(result_tp)
      order_id_tp_market_short = result_tp["data"][0]["algoId"]
      result_sl = tradeAPI.place_algo_order(
          instId="BTC-USDT-SWAP",
          tdMode="cross",
          side="buy",
          posSide="short",
          ordType="conditional",
          sz=size,
          slTriggerPx=slPrice,
          slOrdPx="-1",
          slTriggerPxType="last"
      )
      print(result_sl)
      order_id_sl_market_short = result_sl["data"][0]["algoId"]

      return order_id_market_short
      return order_id_tp_market_short
      return order_id_sl_market_short
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
def get_history_3days():
  result = tradeAPI.get_fills(
      instType = "SWAP"
  )
  print(result)

# История торгов за 3 месяца
def get_history_3months():
  result = tradeAPI.get_fills_history(
      instType = "SWAP"
  )
  print(result)

def calculate_pos_size():
  # Введите свои данные здесь
  x = 10000 # ваш капитал
  L = 20 # леверидж
  risk = 0.03 # риск
  y = 50 # цена входа в сделку
  direction = "long" # направление сделки ("long" или "short")
  volatility = "medium" # волатильность базового актива ("low", "medium" или "high")

  coefficients = {
      "long": {
          "low": 0.98,
          "medium": 0.95,
          "high": 0.90
      },
      "short": {
          "low": 1.02,
          "medium": 1.05,
          "high": 1.10
      }
  }
  # Рассчитываем стоп-лос
  slPrice = enter_price * coefficients[side_of_trade][volatility]
  # Рассчитываем размер позиции
  P = (balance * leverage * risk) / SL
  #   Выводим результаты
  print(f"Стоп-лос: {SL:.2f}")
  print(f"Размер позиции: {P:.2f}")


def check_position():
  result = tradeAPI.get_order(instId="BTC-USDT-SWAP", ordId="676182969496752129")
  print(result)
  enter_price = float(result["data"][0]["avgPx"])
  print(enter_price)

#check_position()
#check_balance()
#place_market_long_order(instId, leverage, size, tpPrice, slPrice, accountAPI)
