from sqlalchemy import Column, Integer, String, Boolean
from datasets.ClassesCreation import Base
from datasets.database import Session


class SQLStateStorage(Base):
    __tablename__ = 'States'
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String)
    TIMEFRAME = Column(String)
    POSITION = Column(String, nullable=True)
    ORDER_ID = Column(String, nullable=True)
    STRATEGY = Column(String)
    STATUS = Column(Boolean)

class StateRequest:
    def __init__(self, intsId=None|str, timeframe=None|str, strategy=None|str):
        self.instId = intsId
        self.timeframe = timeframe
        self.strategy = strategy

    def check_state(self) -> dict:
        # sourcery skip: use-named-expression
        with Session() as session:
            last_state = session.query(SQLStateStorage).filter_by(INST_ID=self.instId, TIMEFRAME=self.timeframe, STRATEGY=self.strategy).first()
            return (
                {
                    'state': last_state.POSITION,
                }
                if last_state
                else {
                    'state': None,
                }
            )


    def update_state(self, new_state:dict) -> None:
        with Session() as session:
            existing_state = session.query(SQLStateStorage).filter_by(
                INST_ID=self.instId, TIMEFRAME=self.timeframe
            ).first()
            existing_state.POSITION = new_state['state']
            existing_state.STATUS = new_state['status']
            existing_state.ORDER_ID = new_state['orderId']
            try:
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()


    def save_position_state(self, new_state:dict) -> None:
        with Session() as session:
            state = SQLStateStorage(
                INST_ID=self.instId,
                TIMEFRAME=self.timeframe,
                POSITION=new_state['state'],
                ORDER_ID=new_state['orderId'],
                STATUS=new_state['status']
            ) 
            session.add(state)
            try:
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()


# State == None
    def save_none_state(self) -> None:
        with Session() as session:
            new_state = SQLStateStorage(
                INST_ID=self.instId,
                TIMEFRAME=self.timeframe,
                POSITION=None,
                ORDER_ID=None,
                STATUS=False,
                STRATEGY = self.strategy
            )
            session.add(new_state)
            try:
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
            



