#libs
import pandas as pd
from typing import Optional, Union
from sqlalchemy.sql import exists
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
#database
from datasets.tables import PositionAndOrders
#utils
from baselogs.custom_logger import create_logger


logger = create_logger('database')



class DataAllDatasets:
    def __init__(self, Session:sessionmaker, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None, test:bool=False):
        self.instId = instId.upper()
        self.timeframe = timeframe.upper()
        self.Session = Session
        self.classes_dict = classes_dict
        self.test = test


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_money_in_deal(self, mapper, connection, target):
        with self.Session():
            target.MONEY_IN_DEAL = target.BALANCE * target.RISK_COEFFICIENT + target.FEE


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_money_income(self, mapper, connection, target):
        with self.Session():
            target.MONEY_INCOME = (target.ENTER_PRICE - target.CLOSE_PRICE) * target.LEVERAGE - target.FEE


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_percent_money_income(self, mapper, connection, target):
        with self.Session():
            target.PERCENT_MONEY_INCOME = (target.MONEY_INCOME / target.BALANCE) * 100


    def get_all_bd_marketdata(self) -> dict:
        if self.test:
            table = self.classes_dict[f'TEST_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with self.Session() as session:
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


    def __if_data_pandas_pd(self, results_dict:Union[dict, pd.DataFrame]) -> dict:
        condition = type(results_dict) == pd.DataFrame
        return {
            'index': results_dict.index.tolist() if condition else results_dict['Date'],
            '_open': results_dict['Open'].tolist() if condition else results_dict['Open'],
            '_close': results_dict['Close'].tolist() if condition else results_dict['Close'],
            'high': results_dict['High'].tolist() if condition else results_dict['High'],
            'low': results_dict['Low'].tolist() if condition else results_dict['Low'],
            'volume': results_dict['Volume'].tolist() if condition else results_dict['Volume'],
            'volume_usdt': [None] * len(results_dict.index) if condition else results_dict['Volume Usdt']
        }



    def save_charts(self, results_dict:Union[dict, pd.DataFrame]) -> None:
        # sourcery skip: class-extract-method
        if self.test:
            table = self.classes_dict[f'TEST_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with self.Session() as session:
            try:
                tags = self.__if_data_pandas_pd(results_dict)
                for i in range(len(tags['index'])):
                    target_data = session.query(exists().where(table.c.TIMESTAMP == tags['index'][i])).scalar()
                    if not target_data:
                        data = table.insert().values(
                            TIMESTAMP=tags['index'][i], INSTRUMENT=self.instId,
                            TIMEFRAME=self.timeframe, OPEN=tags['_open'][i],
                            CLOSE=tags['_close'][i], HIGH=tags['high'][i],
                            LOW=tags['low'][i], VOLUME=tags['volume'][i],
                            VOLUME_USDT=tags['volume_usdt'][i]
                        )
                        session.execute(data)
                        session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()
            


    # Добавление одной строки 
    def add_data_to_db(self, results_dict:dict) -> None:
        if self.test:
            table = self.classes_dict[f'TEST_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with self.Session() as session:
            data = table(
                TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
                TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
                CLOSE=results_dict['Close'], HIGH=results_dict['High'],
                LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
                VOLUME_USDT=results_dict['Volume Usdt']
            )
            if not session.query(exists().where(table.c.TIMESTAMP == data.TIMESTAMP)).scalar():
                session.add(data)
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()


    def save_new_order_data(self, result:dict) -> None:
        with self.Session() as session:
            order_id = PositionAndOrders(
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
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()