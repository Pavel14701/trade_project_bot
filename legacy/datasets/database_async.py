#libs
import asyncio
from typing import Optional
from sqlalchemy.sql import exists
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
#database
from datasets.tables import PositionAndOrders
#utils
from baselogs.custom_logger import create_logger


logger = create_logger(logger_name='DataBaseAsync')


class DataAllDatasetsAsync:
    def __init__(self, Session:AsyncSession, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None, test:bool=False):
        self.instId = instId
        self.timeframe = timeframe
        self.AsyncSessionLocal = Session
        self.classes_dict = classes_dict
        self.test = test


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_money_income(self, mapper, connection, target):
        async with self.AsyncSessionLocal() as session:
            try:
                target.MONEY_INCOME = (target.ENTER_PRICE - target.CLOSE_PRICE) * target.LEVERAGE - target.FEE
            except Exception as e:
                await session.rollback()
                raise e


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_percent_money_income(self, mapper, connection, target):
        async with self.AsyncSessionLocal() as session:
            try:
                target.PERCENT_MONEY_INCOME = (target.MONEY_INCOME / target.BALANCE) * 100
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_money_in_deal(self, mapper, connection, target):
        async with self.AsyncSessionLocal as session:
            try:
                target.MONEY_IN_DEAL = target.BALANCE * target.RISK_COEFFICIENT + target.FEE
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


    async def get_all_bd_marketdata_async(self) -> dict:
        if self.test:
            table = self.classes_dict[f'test_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        async with self.AsyncSessionLocal as session:
            try:
                columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
                query = await session.query(
                    table.c.TIMESTAMP, table.c.OPEN, table.c.CLOSE, table.c.HIGH,
                    table.c.LOW, table.c.VOLUME, table.c.VOLUME_USDT
                ).order_by(table.c.TIMESTAMP).all()
                return {col: [row[i] for row in query] for i, col in enumerate(columns)}
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                await session.aclose()


    async def __process_data_save_charts_async(self, i:int, results_dict:dict, session:AsyncSession, active_class):
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
        if self.test:
            table = self.classes_dict[f'test_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        async with self.AsyncSessionLocal as session:
            try:
                tasks = [
                    self.__process_data_save_charts_async(i, results_dict, session, table)
                    for i in range(len(results_dict['Date']))
                ]
                await asyncio.gather(*tasks)
            except Exception as e:
                logger.error(e)
                await session.rollback()



    # Добавление одной строки 
    async def add_data_to_db_async(self, results_dict: dict) -> None:
        if self.test:
            table = self.classes_dict[f'test_{self.instId}_{self.timeframe}'].__table__
        else:
            table = self.classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        async with self.AsyncSessionLocal as session:
            try:
                data = table(
                    TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
                    TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
                    CLOSE=results_dict['Close'], HIGH=results_dict['High'],
                    LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
                    VOLUME_USDT=results_dict['Volume Usdt']
                )
                exists_query = await session.execute(
                    select(exists().where(table.TIMESTAMP == data.TIMESTAMP))
                )
                if not exists_query.scalar():
                    await session.execute(data)
                    await session.commit()
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                session.aclose()


    async def save_new_order_data_async(self, result:dict) -> None:
        async with self.AsyncSessionLocal as session:
            try:
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
                await session.execute(order_id)
                await session.commit()
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                session.aclose()