#libs
import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from sqlalchemy.sql import exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#database
from DataSets.ClassesCreation import Base, ClassCreation, TradeUserData
#utils
from BaseLogs.CustomDecorators import log_exceptions
from BaseLogs.CustomLogger import create_logger


logger = create_logger(logger_name='DataBase')
engine = create_engine("sqlite:///./datasets/TradeUserDatasets.db")
Session = sessionmaker(bind=engine)
classes_dict = ClassCreation().create_classes(Base)
Base.metadata.create_all(engine)


class DataAllDatasets:
    def __init__(self, instId:Optional[str]=None, timeframe:Optional[str]=None):
        self.instId = instId
        self.timeframe = timeframe


    @log_exceptions(logger)
    def __prosess_data_get_all_bd_marketdata(self, session:sessionmaker, table) -> None:
            query = session.query(
                table.c.TIMESTAMP, table.c.OPEN, table.c.CLOSE,
                table.c.HIGH, table.c.LOW, table.c.VOLUME,
                table.c.VOLUME_USDT
            ).order_by(table.c.TIMESTAMP).all()
            return {
                col: [row[i] for row in query]
                for i, col in enumerate(
                    ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
                )
            }


    def get_all_bd_marketdata(self) -> dict:
        table = classes_dict[f'ChartsData_{self.instId}_{self.timeframe}'].__table__
        with Session() as session:
            self.__prosess_data_get_all_bd_marketdata(session, table)


    @log_exceptions(logger)
    def __process_data_save_charts(self, session:sessionmaker, results_dict:dict, active_class):
        for i in range(len(results_dict,['Date'])):
            target_data = session.query(exists().where(active_class.TIMESTAMP == results_dict['Date'][i])).scalar()
            if not target_data:
                data = active_class(
                    TIMESTAMP=results_dict['Date'][i], INSTRUMENT=self.instId,
                    TIMEFRAME=self.timeframe, OPEN=results_dict['Open'][i],
                    CLOSE=results_dict['Close'][i], HIGH=results_dict['High'][i],
                    LOW=results_dict['Low'][i], VOLUME=results_dict['Volume'][i],
                    VOLUME_USDT=results_dict['Volume Usdt'][i]
                )
                session.add(data)
                session.commit()


    def save_charts(self, results_dict:dict) -> None:
        active_class = classes_dict[f"ChartsData_{self.instId}_{self.timeframe}"]
        with Session() as session:
            self.__process_data_save_charts(session, results_dict, active_class)


    @log_exceptions(logger)
    def __process_data_add_data_to_db(self, session:sessionmaker, results_dict:dict, active_class):
        data = active_class(
            TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
            TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
            CLOSE=results_dict['Close'], HIGH=results_dict['High'],
            LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
            VOLUME_USDT=results_dict['Volume Usdt']
        )
        if not session.query(exists().where(active_class.TIMESTAMP == data.TIMESTAMP)).scalar():
            session.add(data)
            session.commit()


    # Добавление одной строки 
    def add_data_to_db(self, results_dict:dict) -> None:
        active_class = classes_dict[f"ChartsData_{self.instId}_{self.timeframe}"]
        with Session() as session:
            self.__process_data_add_data_to_db(session, results_dict, active_class)


    @log_exceptions(logger)
    def __process_data_save_new_order_data(session:sessionmaker, result:dict):
        order_id = TradeUserData(
            order_id=result['order_id'], status=result['posFlag'],
            order_volume=result['size'], tp_order_volume=result['size'],
            sl_order_volume=result['size'], balance=result['balance'],
            instrument=result['instId'], leverage=result['leverage'],
            side_of_trade=result['posSide'], enter_price=result['enter_price'],
            time=result['outTime'], tp_order_id=result['order_id_tp'],
            tp_price=result['tpPrice'], sl_order_id=result['order_id_sl'],
            sl_price=result['slPrice']
        )
        session.add(order_id)
        session.commit()


    def save_new_order_data(self, result:dict) -> None:
        with Session() as session:
            self.__process_data_save_new_order_data(session, result)