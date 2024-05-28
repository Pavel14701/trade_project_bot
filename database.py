import sqlalchemy
import okx.MarketData as MarketData
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# создаем базовый класс для декларативных классов
Base = declarative_base()
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
# создаем таблицу в базе данных, если она еще не существует
Base.metadata.create_all(engine)
# создаем фабрику сессий
Session = sessionmaker(bind=engine)

create_classes(instIds, timeframes, Base)

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
=======
    return data

>>>>>>> e23f1213a1301559b75c471050618ee99c9687d9
