from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database import Base

class SQLStateStorage(Base):
    __tablename__ = 'States'
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String) #ever(check)
    TIMEFRAME = Column(String) #15m 1h 4h 1d
    POSITION = Column(String, nullable=True) #long or short
    VOLUME = Column(Numeric(10, 4), nullable=True) #ever
    TIME = Column(DateTime) #ever(check)

class StateRequest:
    def __init__(self, IntsId:str, timeframe:str, Session:sessionmaker):
        self.InstId = IntsId
        self.timeframe = timeframe
        self.Session = Session


    def check_state(self):
        with self.Session as session:
                if (
                    last_state := session.query(SQLStateStorage)
                    .filter_by(INST_ID=self.InstId, TIMEFRAME=self.timeframe)
                    .order_by(SQLStateStorage.TIME.desc())
                    .first()
                ):
                    # Упаковка данных в словарь для возврата
                    return {
                        'INST_ID': last_state.INST_ID,
                        'TIMEFRAME': last_state.TIMEFRAME,
                        'POSITION': last_state.POSITION,
                        'VOLUME': float(last_state.VOLUME),
                        'TIME': last_state.TIME.strftime('%Y-%m-%d %H:%M:%S')  # Форматирование даты и времени
                    }
                else:
                    return None


    def save_position_state(self, position, volume):
        with self.Session() as session:
            # Создание нового объекта состояния
            new_state = SQLStateStorage(
                INST_ID=self.InstId,
                TIMEFRAME=self.timeframe,
                POSITION=position,
                VOLUME=volume,
                TIME=datetime.now()  # Запись текущего времени
            )
            # Добавление нового объекта состояния в сессию
            session.add(new_state)
            # Сохранение изменений в базу данных
            session.commit()


    def save_none_state(self):
        with self.Session() as session:
            # Создание нового объекта состояния
            new_state = SQLStateStorage(
                INST_ID=self.InstId,
                TIMEFRAME=self.timeframe,
                POSITION=None,
                VOLUME=None,
                TIME=datetime.now()  # Запись текущего времени
            )
            # Добавление нового объекта состояния в сессию
            session.add(new_state)
            # Сохранение изменений в базу данных
            session.commit()

