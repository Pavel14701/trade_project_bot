#libs
import sys, asyncio
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
#database
from DataSets.ClassesCreation import Base, ClassCreation, TradeUserData
#utils
from BaseLogs.CustomDecorators import log_exceptions_async, retry_on_exception_async
from BaseLogs.CustomLogger import create_logger


logger = create_logger(logger_name='DataBaseAsync')
engine2 = create_async_engine("sqlite+aiosqlite:///./datasets/TradeUserDatasets.db")
AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
classes_dict = ClassCreation().create_classes(Base)
Base.metadata.create_all(engine2)


class DataAllDatasetsAsync:
    def __init__(self, instId:Optional[str]=None, timeframe:Optional[str]=None):
        self.instId = instId
        self.timeframe = timeframe


    @log_exceptions_async(logger)
    @retry_on_exception_async
    async def __process_data_get_all_bd_marketdata_async(self, session:AsyncSession, table):
        columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
        query = await session.query(
                    table.c.TIMESTAMP, table.c.OPEN, table.c.CLOSE, table.c.HIGH,
                    table.c.LOW, table.c.VOLUME, table.c.VOLUME_USDT
                ).order_by(table.c.TIMESTAMP).all()
        return {col: [row[i] for row in query] for i, col in enumerate(columns)}


    async def get_all_bd_marketdata_async(self) -> dict:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        class_ = classes_dict[class_name]
        table = class_.__table__
        async with AsyncSessionLocal() as session:
            return await self.__process_data_get_all_bd_marketdata_async(session, table)


    @log_exceptions_async(logger)
    async def __process_data_save_charts_async(self, i, results_dict, session, active_class):
        target_data = await session.execute(select(exists().where(active_class.TIMESTAMP == results_dict['Date'][i])))
        target_data = target_data.scalar()
        if not target_data:
            data = active_class(
                TIMESTAMP=results_dict['Date'][i], INSTRUMENT=self.instId,
                TIMEFRAME=self.timeframe, OPEN=results_dict['Open'][i],
                CLOSE=results_dict['Close'][i], HIGH=results_dict['High'][i],
                LOW=results_dict['Low'][i], VOLUME=results_dict['Volume'][i],
                VOLUME_USDT=results_dict['Volume Usdt'][i]
            )
            await session.add(data)
            await session.commit()


    async def save_charts_async(self, results_dict: dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = classes_dict[class_name]
        async with AsyncSessionLocal() as session:
            tasks = [
                self.__process_data_save_charts_async(i, results_dict, session, active_class)
                for i in range(len(results_dict['Date']))
            ]
            await asyncio.gather(*tasks)


    @log_exceptions_async(logger)
    async def __process_data_add_data_to_db_async(self, active_class, results_dict:dict, session:AsyncSession) -> None:
        data = active_class(
            TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
            TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
            CLOSE=results_dict['Close'], HIGH=results_dict['High'],
            LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
            VOLUME_USDT=results_dict['Volume Usdt']
        )
        exists_query = await session.execute(
            select(exists().where(active_class.TIMESTAMP == data.TIMESTAMP))
        )
        if not exists_query.scalar():
            await session.add(data)
            await session.commit()


    # Добавление одной строки 
    async def add_data_to_db_async(self, results_dict: dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = classes_dict[class_name]
        async with AsyncSessionLocal() as session:
            await self.__process_data_add_data_to_db_async(active_class, results_dict, session)


    @log_exceptions_async(logger)
    async def __process_data_save_new_order_data_async(self, result:dict, session:AsyncSession) -> None:
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
        await session.add(order_id)
        await session.commit()


    async def save_new_order_data_async(self, result:dict) -> None:
        async with AsyncSessionLocal() as session:
            await self.__process_data_save_new_order_data_async(result, session)