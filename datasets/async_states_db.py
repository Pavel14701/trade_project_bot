#libs
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
#database
from datasets.tables import SQLStateStorage
#utils
from baselogs.custom_logger import create_logger

logger = create_logger('AsyncStatesDB')


class AsyncStateRequest:
    def __init__(self, Session:AsyncSession, IntsId:Optional[str]=None, timeframe:Optional[str]=None):
        self.InstId = IntsId
        self.timeframe = timeframe
        self.AsyncSessionLocal = Session


    async def check_state_async(self) -> dict:
        async with self.AsyncSessionLocal as session:
            try:
                last_state = await session.query(SQLStateStorage).filter_by(
                    INST_ID=self.instId, TIMEFRAME=self.timeframe,
                    STRATEGY=self.strategy
                ).first()
                return ({'state': last_state.POSITION,} if last_state else {'state': None,})
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                await session.aclose()
            
            

    async def update_state_async(self, new_state:dict) -> None:
        async with self.AsyncSessionLocal as session:
            try:
                existing_state = await session.query(SQLStateStorage).filter_by(
                INST_ID=new_state['instId'], ORDER_ID=new_state['orderId']
                ).first()
                existing_state.POSITION = new_state['state']
                existing_state.STATUS = new_state['status']
                existing_state.ORDER_ID = new_state['orderId']
                await session.commit()
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                await session.aclose()


    async def save_position_state_async(self, new_state:dict) -> None:
        async with self.AsyncSessionLocal as session:
            try:
                state = SQLStateStorage(
                    INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=new_state['state'],
                    ORDER_ID=new_state['orderId'], STATUS=new_state['status']
                ) 
                await session.add(state)
                await session.commit()
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                await session.aclose()



    async def save_none_state_async(self) -> None:
        async with self.AsyncSessionLocal as session:
            try:
                new_state = SQLStateStorage(
                    INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=None,
                    ORDER_ID=None, STATUS=False, STRATEGY = self.strategy
                )
                await session.add(new_state)
                await session.commit()
            except Exception as e:
                logger.error(e)
                await session.rollback()
            finally:
                await session.aclose()