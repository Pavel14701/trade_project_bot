#libs
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
#database
from DataSets.ClassesCreation import SQLStateStorage
from DataSets.DataBaseAsync import AsyncSessionLocal
#utils
from Logs.CustomDecorators import log_exceptions_async
from Logs.CustomLogger import create_logger

logger = create_logger('AsyncStatesDB')


class AsyncStateRequest:
    def __init__(self, IntsId:Optional[str]=None, timeframe:Optional[str]=None):
        self.InstId = IntsId
        self.timeframe = timeframe


    @log_exceptions_async(logger)
    async def __process_data_check_state_async(self, session:AsyncSession):
        last_state = await session.query(SQLStateStorage).filter_by(
            INST_ID=self.instId, TIMEFRAME=self.timeframe,
            STRATEGY=self.strategy
        ).first()
        return ({'state': last_state.POSITION,} if last_state else {'state': None,})


    async def check_state_async(self) -> dict:
        with AsyncSessionLocal() as session:
            return await self.__process_data_check_state_async(session)


    @log_exceptions_async(logger)
    async def __process_data_update_state_async(self, session:AsyncSession, new_state:dict) -> None:
        existing_state = await session.query(SQLStateStorage).filter_by(
            INST_ID=new_state['instId'], ORDER_ID=new_state['orderId']
        ).first()
        existing_state.POSITION = new_state['state']
        existing_state.STATUS = new_state['status']
        existing_state.ORDER_ID = new_state['orderId']
        await session.commit()


    async def update_state_async(self, new_state:dict) -> None:
        with AsyncSessionLocal() as session:
            self.__process_data_update_state_async(session, new_state)


    @log_exceptions_async(logger)
    async def __process_data_save_position_state_async(self, session:AsyncSession, new_state:dict) -> None:
        state = SQLStateStorage(
            INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=new_state['state'],
            ORDER_ID=new_state['orderId'], STATUS=new_state['status']
        ) 
        await session.add(state)
        await session.commit()


    async def save_position_state_async(self, new_state:dict) -> None:
        with AsyncSessionLocal() as session:
            await self.__process_data_save_position_state_async(session, new_state)


    @log_exceptions_async(logger)
    async def __process_data_save_none_state_async(self, session:AsyncSession):
        new_state = SQLStateStorage(
            INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=None,
            ORDER_ID=None, STATUS=False, STRATEGY = self.strategy
        )
        await session.add(new_state)
        await session.commit()


    async def save_none_state_async(self) -> None:
        with AsyncSessionLocal() as session:
            await self.__process_data_save_none_state_async(session)