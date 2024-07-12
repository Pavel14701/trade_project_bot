from datasets.StatesDB import SQLStateStorage
from datasets.database import AsyncSessionLocal

class AsyncStateRequest:
    def __init__(self, IntsId=None|str, timeframe=None|str):
        self.InstId = IntsId
        self.timeframe = timeframe


    async def async_update_state(self, new_state:dict) -> None:
        with AsyncSessionLocal() as session:
            existing_state = await session.query(SQLStateStorage).filter_by(
                INST_ID=new_state['instId'], ORDER_ID=new_state['orderId']
            ).first()
            existing_state.POSITION = new_state['state']
            existing_state.STATUS = new_state['status']
            existing_state.ORDER_ID = new_state['orderId']
            try:
                await session.commit()
            except Exception:
                await session.rollback()
            finally:
                await session.close()