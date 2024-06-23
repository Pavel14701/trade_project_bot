from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
from utils.DataLoadSettings import DataLoadSetting

Base = declarative_base()

class SQLStateStorage(Base):
    __tablename__ = 'States'
    SURROGATE_KEY = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String) #ever(check)
    TIMEFRAME = Column(String) #15m 1h 4h 1d
    POSITION = Column(String, nullable=True) #long short
    VOLUME = Column(Numeric(10, 4), nullable=True) #ever
    TIME = Column(DateTime) #ever(check)

class StateRequest(DataLoadSetting):
    def __init__(self, AsyncSessionLocal):
        super().__init__(self.timeframe, self.instId)
        self.AsyncSessionLocal = AsyncSessionLocal


    async def check_state(self):
        async with self.AsyncSessionLocal as session:
            async with session.begin():
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


    async def save_position_state(self, position, volume):
        async with self.AsyncSessionLocal() as session:
            async with session.begin():
                # Создание нового объекта состояния
                new_state = SQLStateStorage(
                    INST_ID=self.InstId,
                    TIMEFRAME=self.timeframe,
                    POSITION=position,
                    VOLUME=volume,
                    TIME=datetime.now()  # Запись текущего времени
                )
                # Добавление нового объекта состояния в сессию
                await session.add(new_state)
                # Сохранение изменений в базу данных
                await session.commit()


    async def save_none_state(self):
        async with self.AsyncSessionLocal() as session:
            async with session.begin():
                # Создание нового объекта состояния
                new_state = SQLStateStorage(
                    INST_ID=self.InstId,
                    TIMEFRAME=self.timeframe,
                    POSITION=None,
                    VOLUME=None,
                    TIME=datetime.now()  # Запись текущего времени
                )
                # Добавление нового объекта состояния в сессию
                await session.add(new_state)
                # Сохранение изменений в базу данных
                await session.commit()

