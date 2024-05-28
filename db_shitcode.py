# импорты
import okx.MarketData as MarketData
from datetime import datetime, timedelta
import sqlalchemy  # pip install sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# данные глобальная область
instId = "BTC-USDT-SWAP"
timeframes = ["15m", "1H", "4H", "1D"]
# Данные Api
flag = "1"
marketDataAPI = MarketData.MarketAPI(flag=flag)
# timeframe = "1D" Минуты с маленькой m, часы H, неделя W, месяц M

# создаем движок для подключения к базе данных
engine = create_engine("sqlite:///drive/MyDrive/charts/TradeUserData.db")  # твой путь
# создаем базовый класс для декларативных классов
Base = declarative_base()


class ChartsData1(Base):
    __tablename__ = "BTC_USDT_SWAP_15MIN"
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TIMESTAMP = Column(DateTime)
    INSTRUMENT = Column(String)
    TIMEFRAME = Column(String)
    OPEN = Column(Numeric(10, 4))
    CLOSE = Column(Numeric(10, 4))
    HIGH = Column(Numeric(10, 4))
    LOW = Column(Numeric(10, 4))
    VOLUME = Column(Numeric(10, 4))
    VOLUME_USDT = Column(Numeric(10, 4))


class ChartsData2(Base):
    __tablename__ = "BTC_USDT_SWAP_1H"
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TIMESTAMP = Column(DateTime)
    INSTRUMENT = Column(String)
    TIMEFRAME = Column(String)
    OPEN = Column(Numeric(10, 4))
    CLOSE = Column(Numeric(10, 4))
    HIGH = Column(Numeric(10, 4))
    LOW = Column(Numeric(10, 4))
    VOLUME = Column(Numeric(10, 4))
    VOLUME_USDT = Column(Numeric(10, 4))


class ChartsData3(Base):
    __tablename__ = "BTC_USDT_SWAP_4H"
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TIMESTAMP = Column(DateTime)
    INSTRUMENT = Column(String)
    TIMEFRAME = Column(String)
    OPEN = Column(Numeric(10, 4))
    CLOSE = Column(Numeric(10, 4))
    HIGH = Column(Numeric(10, 4))
    LOW = Column(Numeric(10, 4))
    VOLUME = Column(Numeric(10, 4))
    VOLUME_USDT = Column(Numeric(10, 4))


class ChartsData4(Base):
    __tablename__ = "BTC_USDT_SWAP_1D"
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    TIMESTAMP = Column(DateTime)
    INSTRUMENT = Column(String)
    TIMEFRAME = Column(String)
    OPEN = Column(Numeric(10, 4))
    CLOSE = Column(Numeric(10, 4))
    HIGH = Column(Numeric(10, 4))
    LOW = Column(Numeric(10, 4))
    VOLUME = Column(Numeric(10, 4))
    VOLUME_USDT = Column(Numeric(10, 4))


# создаем таблицу в базе данных, если она еще не существует
Base.metadata.create_all(engine)
# создаем фабрику сессий
Session = sessionmaker(bind=engine)
