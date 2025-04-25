#libs
import itertools, numpy as np
from typing import Tuple, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Boolean, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from psycopg2.extensions import AsIs, register_adapter
#configs
from configs.load_settings import ConfigsProvider


Base = declarative_base()


class ClassCreation:
    def __init__(self, test:bool=False, instId:Optional[str]=None, timeframe:Optional[str]=None):
        self.user_settings = ConfigsProvider().load_user_configs()
        self.test = test
        self.instId = instId.upper()
        self.timeframe = timeframe.upper()


    def create_classes(self, Base):
        if self.test:
            return self.__create_classes_test(Base)
        return self.__create_classes_no_test(Base)


    def __create_classes_no_test(self, Base):
        classes = {}
        instIds = set(self.user_settings['instIds'])
        timeframes = set(self.user_settings['timeframes'])
        for inst_id, timeframe in itertools.product(instIds, timeframes):
                class_name = f"{inst_id}_{timeframe}"
                table_name = f"{inst_id}_{timeframe}"
                class_ = type(class_name, (Base,), {
                    '__tablename__': table_name,
                    '__table_args__': {'extend_existing': True},
                    'TIMESTAMP': Column(DateTime, primary_key=True),
                    'INSTRUMENT': Column(String),
                    'TIMEFRAME': Column(String),
                    'OPEN': Column(Numeric(30,10)),
                    'CLOSE': Column(Numeric(30,10)),
                    'HIGH': Column(Numeric(30,10)),
                    'LOW': Column(Numeric(30,10)),
                    'VOLUME': Column(Numeric(30,10)),
                    'VOLUME_USDT': Column(Numeric(30,10))
                })
                classes[class_name] = class_
        return classes


    def __create_classes_test(self, Base):
        class_name = f"TEST_{self.instId}_{self.timeframe}"
        table_name = f"TEST_{self.instId}_{self.timeframe}"
        class_ = type(class_name, (Base,), {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True},
            'TIMESTAMP': Column(DateTime, primary_key=True),
            'INSTRUMENT': Column(String),
            'TIMEFRAME': Column(String),
            'OPEN': Column(Numeric(30,10)),
            'CLOSE': Column(Numeric(30,10)),
            'HIGH': Column(Numeric(30,10)),
            'LOW': Column(Numeric(30,10)),
            'VOLUME': Column(Numeric(30,10)),
            'VOLUME_USDT': Column(Numeric(30,10))
        })
        return {class_name: class_}


class PositionAndOrders(Base):
    __tablename__ = 'POSITIONS_AND_ORDERS'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    ORDER_ID = Column(String, nullable=False)
    INSTRUMENT = Column(String)
    SIDE_OF_TRADE = Column(String)
    LEVERAGE = Column(Integer)
    OPEN_TIME = Column(DateTime)
    CLOSE_TIME = Column(DateTime, nullable=True)
    STATUS = Column(Boolean)
    BALANCE = Column(Integer)
    PRICE_OF_CONTRACT = Column(Float)
    NUMBER_OF_CONTRACTS = Column(Float)
    MONEY_IN_DEAL = Column(Float, nullable=True)
    ENTER_PRICE = Column(Float, nullable=True)
    ORDER_VOLUME = Column(Float)
    TAKEPROFIT_PRICE = Column(Float, nullable=True)
    TAKEPROFIT_ORDER_ID = Column(String, nullable=True)
    TAKEPROFIT_ORDER_VOLUME = Column(Float, nullable=True)
    STOPLOSS_PRICE = Column(Float)
    STOPLOSS_ORDER_ID = Column(String)
    STOPLOSS_ORDER_VOLUME = Column(Float)
    RISK_COEFFICIENT = Column(Float)
    CLOSE_PRICE = Column(Float, nullable=True)
    FEE = Column(Float, nullable=True)
    MONEY_INCOME = Column(Float, nullable=True)
    PERCENT_MONEY_INCOME = Column(Float, nullable=True)


class SQLStateStorage(Base):
    __tablename__ = 'STATES'
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String)
    TIMEFRAME = Column(String)
    POSITION = Column(String, nullable=True)
    ORDER_ID = Column(String, nullable=True)
    STRATEGY = Column(String)
    STATUS = Column(Boolean)


def create_tables(test:bool=False, instId:Optional[str]=None, timeframe:Optional[str]=None) -> Tuple[sessionmaker, dict]:
    register_adapter(np.int64, addapt_numpy_int64)
    engine = create_engine('postgresql://postgres:admin1234@localhost/trade_user_data')
    classes_dict = ClassCreation(test, instId, timeframe).create_classes(Base)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return (Session, classes_dict)


async def create_tables_async(test:bool=False, instId:Optional[str]=None, timeframe:Optional[str]=None) -> Tuple[AsyncSession, dict]:
    register_adapter(np.int64, addapt_numpy_int64)
    engine2 = create_async_engine('postgresql+asyncpg://postgres:admin1234@localhost/trade_user_data')
    AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
    classes_dict = ClassCreation(test, instId, timeframe).create_classes(Base)
    async with engine2.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return (AsyncSessionLocal , classes_dict)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)