import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from sqlalchemy.sql import exists
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datasets.StatesDB import SQLStateStorage
from sqlalchemy.orm import sessionmaker
from User.LoadSettings import LoadUserSettingData
from datasets.ClassesCreation import ClassCreation, TradeUserData, Base
from utils.DataFrameUtils import prepare_many_data_to_append_db


engine1 = create_engine("sqlite:///./datasets/TradeUserDatasets.db")
engine2 = create_async_engine("sqlite+aiosqlite:///./datasets/TradeUserDatasets.db")

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
Session = sessionmaker(bind=engine1)



def create_classes(Base):
    classes_dict = ClassCreation().create_classes(Base)
    Base.metadata.create_all(engine1)
    return classes_dict

classes_dict = create_classes(Base)
    


class DataAllDatasets(LoadUserSettingData):
    def __init__(
        self, instId=None|str, timeframe=None|str, Session=None|sessionmaker, classes_dict=None):
        super().__init__()
        self.instId = instId
        self.timeframe = timeframe
        self.Session = Session
        self.classes_dict = classes_dict


    def get_bd_marketdata(self) -> dict:
        # sourcery skip: collection-builtin-to-comprehension
        data = {}
        for timeframe in self.timeframes:
            class_name = f"ChartsData_{self.instId}_{self.timeframe}"
            class_ = self.classes_dict[class_name]
            table = class_.mapper.mapped_table
            with self.Session() as session:
                query = session.query(
                    table.c.TIMESTAMP,
                    table.c.OPEN,
                    table.c.CLOSE,
                    table.c.HIGH,
                    table.c.LOW,
                    table.c.VOLUME,
                    table.c.VOLUME_USDT
                ).all()
            d = dict(
                (col, [row[i] for row in query]) for i, col in enumerate(
                    ['date', 'open', 'close', 'high', 'low', 'volume', 'volume_usdt']
                    ))
            data[timeframe] = d
        return data


    def save_charts(self, result:dict) -> None:
        # sourcery skip: extract-method, merge-list-append, move-assign-in-block
        results_dict = prepare_many_data_to_append_db(result)
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = self.classes_dict[class_name]
        with self.Session() as session:
            for i in range(len(results_dict['time'])):
                target_data = session.query(exists().where(active_class.TIMESTAMP == results_dict['time'][i])).scalar()
                if not target_data:
                    data = active_class(
                        TIMESTAMP=results_dict['time'][i],
                        INSTRUMENT=self.instId,
                        TIMEFRAME=self.timeframe,
                        OPEN=results_dict['open'][i],
                        CLOSE=results_dict['close'][i],
                        HIGH=results_dict['high'][i],
                        LOW=results_dict['low'][i],
                        VOLUME=results_dict['volume'][i],
                        VOLUME_USDT=results_dict['volume_usdt'][i]
                    )
                    session.add(data)
                    try:
                        session.commit()
                    except Exception:
                        session.rollback()
                    finally:
                        session.close()


    def add_data_to_db(self, data_list:dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = self.classes_dict[class_name]
        with self.Session() as session:
            for data_dict in data_list:
                for i in data_dict['time']:
                    data = active_class(
                        TIMESTAMP=data_dict['time'][i],
                        INSTRUMENT=self.instId,
                        TIMEFRAME=self.timeframe,
                        OPEN=data_dict['open'][i],
                        CLOSE=data_dict['close'][i],
                        HIGH=data_dict['high'][i],
                        LOW=data_dict['low'][i],
                        VOLUME=data_dict['volume'][i],
                        VOLUME_USDT=data_dict['volume'][i]
                    )
                    if not session.query(exists().where(active_class.TIMESTAMP == data.TIMESTAMP)).scalar():
                        session.add(data)
                        try:
                            session.commit()
                        except Exception:
                            session.rollback()
                        finally:
                            session.close()


    def save_new_order_data(self, result:dict) -> None:
        with self.Session as session:
            order_id = TradeUserData(
                order_id=result['order_id'],
                status=result['posFlag'],
                order_volume=result['size'],
                tp_order_volume=result['size'],
                sl_order_volume=result['size'],
                balance=result['balance'],
                instrument=result['instId'],
                leverage=result['leverage'],
                side_of_trade=result['posSide'],
                enter_price=result['enter_price'],
                time=result['outTime'],
                tp_order_id=result['order_id_tp'],
                tp_price=result['tpPrice'],
                sl_order_id=result['order_id_sl'],
                sl_price=result['slPrice']
            )
            session.add(order_id)
            try:
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()



