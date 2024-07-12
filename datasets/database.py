import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from sqlalchemy.sql import exists
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from User.LoadSettings import LoadUserSettingData
from datasets.ClassesCreation import ClassCreation, TradeUserData, Base
from utils.DataFrameUtils import prepare_many_data_to_append_db


engine1 = create_engine("sqlite:///./datasets/TradeUserDatasets.db")
engine2 = create_async_engine("sqlite+aiosqlite:///./datasets/TradeUserDatasets.db")

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
Session = sessionmaker(bind=engine1)



def create_classes(Base):
    classes_dict = ClassCreation().create_classes(Base)
    Base.metadata.create_all(engine1)
    return classes_dict

classes_dict = create_classes(Base)
    


class DataAllDatasets(LoadUserSettingData):
    def __init__(
        self, instId=None|str, timeframe=None|str):
        super().__init__()
        self.instId = instId
        self.timeframe = timeframe


    def get_all_bd_marketdata(self) -> dict:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        class_ = classes_dict[class_name]
        table = class_.__table__
        with Session() as session:
            query = session.query(
                table.c.TIMESTAMP,
                table.c.OPEN,
                table.c.CLOSE,
                table.c.HIGH,
                table.c.LOW,
                table.c.VOLUME,
                table.c.VOLUME_USDT
            ).order_by(table.c.TIMESTAMP).all()
        return {
            col: [row[i] for row in query]
            for i, col in enumerate(
                ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
            )
        }



    def save_charts(self, results_dict:dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = classes_dict[class_name]
        with Session() as session:
            for i in range(len(results_dict['time'])):
                target_data = session.query(exists().where(active_class.TIMESTAMP == results_dict['time'][i])).scalar()
                if not target_data:
                    data = active_class(
                        TIMESTAMP=results_dict['Date'][i],
                        INSTRUMENT=self.instId,
                        TIMEFRAME=self.timeframe,
                        OPEN=results_dict['Open'][i],
                        CLOSE=results_dict['Close'][i],
                        HIGH=results_dict['High'][i],
                        LOW=results_dict['Low'][i],
                        VOLUME=results_dict['Volume'][i],
                        VOLUME_USDT=results_dict['Volume Usdt'][i]
                    )
                    session.add(data)
                    try:
                        session.commit()
                    except Exception:
                        session.rollback()
                    finally:
                        session.close()


    def add_data_to_db(self, results_dict:dict) -> None:
        class_name = f"ChartsData_{self.instId}_{self.timeframe}"
        active_class = classes_dict[class_name]
        with Session() as session:
            data = active_class(
                TIMESTAMP=results_dict['Date'],
                INSTRUMENT=self.instId,
                TIMEFRAME=self.timeframe,
                OPEN=results_dict['Open'],
                CLOSE=results_dict['Close'],
                HIGH=results_dict['High'],
                LOW=results_dict['Low'],
                VOLUME=results_dict['Volume'],
                VOLUME_USDT=results_dict['Volume Usdt']
            )
            if not session.query(exists().where(active_class.TIMESTAMP == data.TIMESTAMP)).scalar():
                session.add(data)
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                finally:
                    session.close()


    def save_new_order_data(self, result:dict) -> None:
        with Session() as session:
            order_id = TradeUserData(
                order_id=result['order_id'],
                status=result['posFlag'],
                order_volume=result['size'],
                tp_order_volume=result['size'],
                sl_order_volume=result['size'],
                balance=result['balance'],
                instrument=result['instId'],
                leverage=result['leverage'],
                side_of_trade=result['posSide'],
                enter_price=result['enter_price'],
                time=result['outTime'],
                tp_order_id=result['order_id_tp'],
                tp_price=result['tpPrice'],
                sl_order_id=result['order_id_sl'],
                sl_price=result['slPrice']
            )
            session.add(order_id)
            try:
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()



