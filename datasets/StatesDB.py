from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database import Base
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('states.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class SQLStateStorage(Base):
    __tablename__ = 'States'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String) #ever(check)
    TIMEFRAME = Column(String) #15m 1h 4h 1d
    POSITION = Column(String, nullable=True) #long or short
    VOLUME = Column(Numeric(10, 4), nullable=True) #ever
    TIME = Column(DateTime) #ever(check)
    STATUS = Column(Boolean)

class StateRequest:
    def __init__(self, IntsId:str, timeframe:str, Session:sessionmaker):
        self.InstId = IntsId
        self.timeframe = timeframe
        self.Session = Session

# нужно ввести сортировку не просто последнего стейта, а последнего по по времени, таймфрейму
# и инструменту

    def check_state(self) -> dict:
        with self.Session as session:
            try:
                if (
                    last_state := session.query(SQLStateStorage)
                    .filter_by(INST_ID=self.InstId, TIMEFRAME=self.timeframe)
                    .order_by(SQLStateStorage.TIME.desc())
                    .first()
                ):
                    return {
                        'id': last_state.ID,
                        'instId': last_state.INST_ID,
                        'timeframe': last_state.TIMEFRAME,
                        'position': last_state.POSITION,
                        'volume': float(last_state.VOLUME),
                        'time': last_state.TIME.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': last_state.STATUS
                    }
                else:
                    return None
            except Exception as e:
                logger.error(f" \n{datetime.datetime.now().isoformat()} Error check state:\n{e}")


    def update_state(self, new_state:dict) -> None:
        with self.Session as session:
            try:
                existing_state = session.query(SQLStateStorage).filter_by(
                    INST_ID=self.InstId, TIMEFRAME=self.timeframe
                ).first()
                existing_state.POSITION = new_state['position']
                existing_state.VOLUME = new_state['volume']
                existing_state.STATUS = new_state['status']
                session.commit()
            except Exception as e:
                logger.error(f"\n{datetime.datetime.now().isoformat()} Error update state:\n{e}")


    def save_position_state(self, position, volume):
        with self.Session() as session:
            new_state = SQLStateStorage(
                INST_ID=self.InstId,
                TIMEFRAME=self.timeframe,
                POSITION=position,
                VOLUME=volume,
                TIME=datetime.now()
            )
            try:    
                session.add(new_state)
                session.commit()
            except Exception as e:
                logger.error(f"\n{datetime.datetime.now().isoformat()} Error save position state:\n{e}")
                session.rollback()
            finally:
                session.close()

# State == None
    def save_none_state(self):
        with self.Session() as session:
            new_state = SQLStateStorage(
                INST_ID=self.InstId,
                TIMEFRAME=self.timeframe,
                POSITION=None,
                VOLUME=None,
                TIME=datetime.now(),
                STATUS=False
            )
            try:    
                session.add(new_state)
                session.commit()
            except Exception as e:
                logger.error(f"\n{datetime.datetime.now().isoformat()} Error save none state:\n{e}")
                session.rollback()
            finally:
                session.close()