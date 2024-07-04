import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from sqlalchemy.sql import exists
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from User.LoadSettings import LoadUserSettingData
from User.UserInfoFunctions import UserInfo
from datasets.ClassesCreation import ClassCreation
from utils.DataFrameUtils import prepare_many_data_to_append_db


engine1 = create_engine("sqlite:///./datasets/TradeUserDatasets.db")
engine2 = create_async_engine("sqlite+aiosqlite:///./datasets/TradeUserDatasets.db")

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
Base = declarative_base()
Session = sessionmaker(bind=engine1)


async def create_tables(Base): 
    data_all_datasets = ClassCreation()
    TradeUserData = data_all_datasets.create_TradeUserData(Base)
    async with engine2.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return TradeUserData


def create_classes(Base):
    data_all_datasets = ClassCreation()
    classes_dict = data_all_datasets.create_classes(Base)
    TradeUserData = data_all_datasets.create_TradeUserData(Base)
    Base.metadata.create_all(engine1)
    return classes_dict, TradeUserData
    


class DataAllDatasets(UserInfo, ClassCreation, LoadUserSettingData):
    def __init__(
        self, instId=None|str, timeframe=None|str, Session=None|sessionmaker, classes_dict=None,
        load_data_after=None|str, load_data_before=None|str, lenghts=None|int):
        super().__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        self.Session = Session
        self.classes_dict = classes_dict


    def get_bd_marketdata(self) -> dict:
        # sourcery skip: collection-builtin-to-comprehension
        data = {}
        for timeframe in self.timeframes:
            class_name = f"ChartsData_{self.instId}_{self.timeframe}"
            class_ = self.classes_dict[class_name]
            table_name = class_.mapper.mapped_table.name
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


    def get_charts(self) -> None:
        # sourcery skip: extract-method, merge-list-append, move-assign-in-block
        results_list = []
        for instId in self.instIds:
            for timeframe in self.timeframes:
                result = super().get_market_data()
                for i in range(len(result['data'])):
                    data_dict = prepare_many_data_to_append_db(result, i, instId, timeframe)
                    results_list.append(data_dict)
        class_name = f"ChartsData_{instId}_{timeframe}"
        active_class = self.classes_dict[class_name]
        with self.Session() as session:
            for i in len(data_dict['time']):
                target_data = session.query(exists().where(active_class.TIMESTAMP == data_dict['time'][i])).scalar()
                if not target_data:
                    data = active_class(
                        TIMESTAMP=data_dict['time'][i],
                        INSTRUMENT=data_dict['instId'][i],
                        TIMEFRAME=data_dict['timeframe'][i],
                        OPEN=data_dict['open'][i],
                        CLOSE=data_dict['close'][i],
                        HIGH=data_dict['high'][i],
                        LOW=data_dict['low'][i],
                        VOLUME=data_dict['volume'][i],
                        VOLUME_USDT=data_dict['volume_usdt'][i]
                    )
                    session.add(data)
                    try:
                        session.commit()
                    except Exception as e:
                        print(f'Произошла ошибка: {e}')
                        session.rollback()
                    finally:
                        session.close()


    def add_data_to_db(self, data_list:dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = self.classes_dict[class_name]
        with self.Session() as session:
            for data_dict in data_list:
                for i in len(data_dict['time']):
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
                    except Exception as e:
                        print(f"Ошибка при добавлении данных: {e}")
                        session.rollback()
                    finally:
                        session.close()