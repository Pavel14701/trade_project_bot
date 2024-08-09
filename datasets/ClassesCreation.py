#libs
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Float
from sqlalchemy.orm import declarative_base
#configs
from Configs.LoadSettings import LoadUserSettingData
from Logs.CustomDecorators import log_exceptions
from Logs.CustomLogger import create_logger

logger = create_logger('ClassesCreation')
Base = declarative_base()


class ClassCreation:
    def __init__(self):
        self.user_settings = LoadUserSettingData().load_user_settings()

    @log_exceptions(logger)
    def create_classes(self, Base):
        classes = {}
        for inst_id in self.user_settings['instIds']:
            for timeframe in self.user_settings['timeframes']:
                class_name = f"ChartsData_{inst_id}_{timeframe}"
                table_name = f"{inst_id}_{timeframe}"
                class_ = type(class_name, (Base,), {
                    '__tablename__': table_name,
                    '__table_args__': {'extend_existing': True},
                    'TIMESTAMP': Column(DateTime, primary_key=True),
                    'INSTRUMENT': Column(String),
                    'TIMEFRAME': Column(String),
                    'OPEN': Column(Numeric(10, 4)),
                    'CLOSE': Column(Numeric(10, 4)),
                    'HIGH': Column(Numeric(10, 4)),
                    'LOW': Column(Numeric(10, 4)),
                    'VOLUME': Column(Numeric(10, 4)),
                    'VOLUME_USDT': Column(Numeric(10, 4))
                })
                classes[class_name] = class_
        return classes


#добавлена автоинкрементируемая ячейка для создания доступа к таймфрему в процессе родителе
#теперь при создании объекта ордера, доступ к данным таймфрема можно будет получить по 
# уникальному инкрементируемому id(в теории)-> Похуй
class TradeUserData(Base):
    __tablename__ = 'PositionAndOrders'
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, autoincrement=True)
    ORDER_ID = Column(String, primary_key=True)
    INSTRUMENT = Column(String)
    SIDE_OF_TRADE = Column(String)
    LEVERAGE = Column(Integer)
    OPEN_TIME = Column(DateTime)
    CLOSE_TIME = Column(DateTime, nullable=True)
    STATUS = Column(Boolean)
    BALANCE = Column(Integer)
    PRICE_OF_CONTRAC = Column(Float)
    NUMBER_OF_CONTRACTS = Column(Float)
    MONEY_IN_DEAL = Column(Float, server_default='BALANCE*RISK_COEFFICIENT+FEE', nullable=True)
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
    MONEY_INCOME = Column(Float, server_default='(ENTER_PRICE-CLOSE_PRICE)*LEVERAGE-FEE', nullable=True)
    PERCENT_MONEY_INCOME = Column(Float, server_default='MONEY_INCOME/BALANCE*100', nullable=True)


class SQLStateStorage(Base):
    __tablename__ = 'States'
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String)
    TIMEFRAME = Column(String)
    POSITION = Column(String, nullable=True)
    ORDER_ID = Column(String, nullable=True)
    STRATEGY = Column(String)
    STATUS = Column(Boolean)