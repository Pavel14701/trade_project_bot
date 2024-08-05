from typing import Optional
from sqlalchemy.orm import sessionmaker
from datasets.ClassesCreation import SQLStateStorage
from datasets.DataBase import Session
from utils.CustomLogger import create_logger
from utils.CustomDecorators import log_exceptions
logger = create_logger('StatesDb')


class StateRequest:
    def __init__(
        self, intsId:Optional[str]=None, timeframe:Optional[str]=None,
        strategy:Optional[str]=None
        ):
        self.instId = intsId
        self.timeframe = timeframe
        self.strategy = strategy

    @log_exceptions(logger)
    def process_data_check_state(self, session:sessionmaker):
        last_state = session.query(SQLStateStorage).filter_by(
            INST_ID=self.instId, TIMEFRAME=self.timeframe,
            STRATEGY=self.strategy
        ).first()
        return ({'state': last_state.POSITION,} if last_state else {'state': None,})


    def check_state(self) -> dict:
        with Session() as session:
            return self.process_data_check_state(session)


    @log_exceptions(logger)
    def process_data_update_state(self, session:sessionmaker, new_state:dict):
        existing_state = session.query(SQLStateStorage).filter_by(
            INST_ID=self.instId, TIMEFRAME=self.timeframe
        ).first()
        existing_state.POSITION = new_state['state']
        existing_state.STATUS = new_state['status']
        existing_state.ORDER_ID = new_state['orderId']
        session.commit()


    def update_state(self, new_state:dict) -> None:
        with Session() as session:
            self.process_data_update_state(session, new_state)


    @log_exceptions(logger)
    def process_data_save_position_state(self, session:sessionmaker, new_state:dict) -> None:
        state = SQLStateStorage(
            INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=new_state['state'],
            ORDER_ID=new_state['orderId'], STATUS=new_state['status']
        ) 
        session.add(state)
        session.commit()


    def save_position_state(self, new_state:dict) -> None:
        with Session() as session:
            self.process_data_save_position_state(session, new_state)


    @log_exceptions(logger)
    def process_data_save_none_state(self, session):
        new_state = SQLStateStorage(
            INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=None,
            ORDER_ID=None, STATUS=False, STRATEGY = self.strategy
        )
        session.add(new_state)
        session.commit()


    def save_none_state(self) -> None:
        with Session() as session:
            self.process_data_save_none_state(session)



