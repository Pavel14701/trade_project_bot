import sqlalchemy
import okx.MarketData as MarketData
from sqlalchemy import create_engine,Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

instIds = ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]
timeframes = ("15m", "1H", "4H", "1D")
flag = "1"
marketDataAPI = MarketData.MarketAPI(flag=flag)
#timeframe = "1D" Минуты с маленькой m, часы H, неделя W, месяц M

engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserData.db")#твой путь
# создаем базовый класс для декларативных классов
Base = declarative_base()


# Функция для создания классов с заданными параметрами
def create_classes(instIds, timeframes, Base):
    classes = {}
    for inst_id in instIds:
        for timeframe in timeframes:
            class_name = f"ChartsData_{inst_id}_{timeframe}"
            table_name = f"{inst_id}_{timeframe}"
            class_ = type(class_name, (Base,), {
                "__tablename__": table_name,
                "SURROGATE_KEY": Column(Integer, primary_key=True, autoincrement=True),
                "TIMESTAMP": Column(DateTime),
                "INSTRUMENT": Column(String),
                "TIMEFRAME": Column(String),
                "OPEN": Column(Numeric(10, 4)),
                "CLOSE": Column(Numeric(10, 4)),
                "HIGH": Column(Numeric(10, 4)),
                "LOW": Column(Numeric(10, 4)),
                "VOLUME": Column(Numeric(10, 4)),
                "VOLUME_USDT": Column(Numeric(10, 4))
            })
            classes[class_name] = class_
    print(classes)
    return classes

create_classes(instIds, timeframes, Base)

class TradeUserData(Base):
    __tablename__ = "positions_and_orders"
    order_id = Column(String, primary_key=True)
    balance = Column(Integer)
    instrument = Column(String)
    enter_price = Column(Numeric(10, 4))
    price_of_1contr = Column(Numeric(10, 4))
    number_of_contracts = Column(Numeric(10, 4))
    money_in_deal = Column(Integer)
    side_of_trade = Column(String)
    order_volume = Column(Integer)
    leverage = Column(Integer)
    time = Column(DateTime)
    status = Column(Boolean)
    tp_price = Column(Numeric(10, 4))
    tp_order_id = Column(String)
    tp_order_volume = Column(Integer)
    sl_price = Column(Numeric(10, 4))
    sl_order_id = Column(String)
    sl_order_volume = Column(Integer)
    risk_coef = Column(Numeric(10, 4))
    close_price = Column(Numeric(10, 4))
    money_income = Column(Integer)
    percent_money_income = Column(Numeric(10, 4))


# создаем таблицу в базе данных, если она еще не существует
Base.metadata.create_all(engine)
# создаем фабрику сессий
Session = sessionmaker(bind=engine)


# Вывод данных из бд в дикте
# Метод для получения данных из таблиц
def get_data(instId, timeframes, classes):
    # Создаем пустой словарь для хранения данных
    data = {}
    # Проходим по всем комбинациям инструментов и временных интервалов
    for timeframe in timeframes:
        # Создаем сессию
        session = Session()
        # Получаем класс по имени
        class_name = f"ChartsData_{instId}_{timeframe}"
        class_ = classes[class_name]
        # Получаем имя таблицы по классу
        table_name = class_.mapper.mapped_table.name
        # Получаем объект таблицы по классу
        table = class_.mapper.mapped_table
        # Используем метод c для доступа к колонкам таблицы
        query = session.query(
            table.c.TIMESTAMP,
            table.c.OPEN,
            table.c.CLOSE,
            table.c.HIGH,
            table.c.LOW,
            table.c.VOLUME,
            table.c.VOLUME_USDT
        ).all()
        # Закрываем сессию
        session.close()
        # Преобразуем результат в словарь
        d = dict((col, [row[i] for row in query]) for i, col in enumerate(['date', 'open', 'close', 'high', 'low', 'volume', 'volume_usdt']))
        # Добавляем ключ и значение в словарь
        data[timeframe] = d
    # Возвращаем словарь данных
    print(data)
    return data

# Запрос на получение последних данных из биржи
def get_charts(instId, timeframes, marketDataAPI):
    for timeframe in timeframes:
        lenghts = 300 #Лимит Okx на 1 реквест
        result = marketDataAPI.get_candlesticks(
            instId=instId,
            after="",
            before="",
            bar=timeframe,
            limit=lenghts
        )
        print(result)
        for i in range(0, 299):
            time = int(result["data"][i][0])
            time = time / 1000
            time = datetime.fromtimestamp(time)
            time = time + timedelta(hours=3)
            open = result["data"][i][1]
            close = result["data"][i][2]
            high = result["data"][i][3]
            low = result["data"][i][4]
            volume = result["data"][i][6]
            volume_usdt = result["data"][i][7]
            # Формируем объект data для отправки в бд
            if timeframe == "15m":
                data = ChartsData1(
                    TIMESTAMP=time,
                    INSTRUMENT=instId,
                    TIMEFRAME=timeframe,
                    OPEN=open,
                    CLOSE=close,
                    HIGH=high,
                    LOW=low,
                    VOLUME=volume,
                    VOLUME_USDT=volume_usdt
                )
                #Сохраняем данные в бд
                session.add(data)
                #Применяем изменения
                session.commit()
                session.close()
            elif timeframe == "1H":
                data = ChartsData2(
                    TIMESTAMP=time,
                    INSTRUMENT=instId,
                    TIMEFRAME=timeframe,
                    OPEN=open,
                    CLOSE=close,
                    HIGH=high,
                    LOW=low,
                    VOLUME=volume,
                    VOLUME_USDT=volume_usdt
                )
                #Сохраняем данные в бд
                session.add(data)
                #Применяем изменения
                session.commit()
                session.close()
            elif timeframe == "4H":
                data = ChartsData3(
                    TIMESTAMP=time,
                    INSTRUMENT=instId,
                    TIMEFRAME=timeframe,
                    OPEN=open,
                    CLOSE=close,
                    HIGH=high,
                    LOW=low,
                    VOLUME=volume,
                    VOLUME_USDT=volume_usdt
                )
                #Сохраняем данные в бд
                session.add(data)
                #Применяем изменения
                session.commit()
                session.close()
            elif timeframe == "1D":
                data = ChartsData4(
                    TIMESTAMP=time,
                    INSTRUMENT=instId,
                    TIMEFRAME=timeframe,
                    OPEN=open,
                    CLOSE=close,
                    HIGH=high,
                    LOW=low,
                    VOLUME=volume,
                    VOLUME_USDT=volume_usdt
                )
                #Сохраняем данные в бд
                session.add(data)
                #Применяем изменения
                session.commit()
                session.close()
