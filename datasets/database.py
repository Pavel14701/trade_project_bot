from sqlalchemy.sql import exists
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
import pandas as pd
from datetime import datetime, timedelta
from okx import MarketData


class DataAllDatasets:
    """
    Initializes DataAllDatasets with provided parameters.

    Args:
        instIds: List of instrument IDs.
        flag: Flag for DataAllDatasets.
        timeframes: List of timeframes.
        Session: Session for database interaction.

    Returns:
        None.
    """
    def __init__(self, instIds, flag, timeframes, Session=None):
        self.instIds = instIds
        self.timeframes = timeframes
        self.Session = Session
        self.flag = flag


    # Функция для создания классов с заданными параметрами
    def create_classes(self, Base):
        """
        Creates classes with specified parameters.

        Args:
            Base: The base class for creating classes.

        Returns:
            A dictionary containing created classes.
        """
        classes = {}
        for inst_id in self.instIds:
            for timeframe in self.timeframes:
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

    
    def create_TradeUserData(self, Base):
        """
        Creates a TradeUserData class for managing positions and orders.

        Args:
            Base: The base class for TradeUserData.

        Returns:
            The TradeUserData class.
        """
        # sourcery skip: inline-immediately-returned-variable
        class_name = "TradeUserData"
        table_name = "positions_and_orders"
        class_ = type(class_name, (Base,), {
            "__tablename__": table_name,
            "__table_args__": {'extend_existing': True},
            "order_id": Column(String, primary_key=True),
            "balance": Column(Integer),
            "instrument": Column(String),
            "enter_price": Column(Numeric(10, 4)),
            "price_of_1contr": Column(Numeric(10, 4)),
            "number_of_contracts": Column(Numeric(10, 4)),
            "money_in_deal": Column(Integer),
            "side_of_trade": Column(String),
            "order_volume": Column(Integer),
            "leverage":  Column(Integer),
            "time" : Column(DateTime),
            "status": Column(Boolean),
            "tp_price": Column(Numeric(10, 4)),
            "tp_order_id": Column(String),
            "tp_order_volume": Column(Integer),
            "sl_price": Column(Numeric(10, 4)),
            "sl_order_id": Column(String),
            "sl_order_volume": Column(Integer),
            "risk_coef": Column(Numeric(10, 4)),
            "close_price": Column(Numeric(10, 4)),
            "money_income": Column(Integer),
            "percent_money_income": Column(Numeric(10, 4))
        })
        TradeUserData = class_
        return TradeUserData

    
    # Вывод данных из бд в дикте
    # Метод для получения данных из таблиц
    def get_bd_marketdata(self, classes, timeframe):
        """
        Retrieves market data from tables.

        Args:
            classes: A dictionary containing classes.
            timeframe: The timeframe to retrieve data for.

        Returns:
            A dictionary containing market data.

        Raises:
            None.
        """
        # sourcery skip: collection-builtin-to-comprehension
        # Создаем пустой словарь для хранения данных
        data = {}
        # Проходим по всем комбинациям инструментов и временных интервалов
        for timeframe in self.timeframes:
            # Получаем класс по имени
            class_name = f"ChartsData_{self.instId}_{timeframe}"
            class_ = classes[class_name]
            # Получаем имя таблицы по классу
            table_name = class_.mapper.mapped_table.name
            # Получаем объект таблицы по классу
            table = class_.mapper.mapped_table
            # Используем метод c для доступа к колонкам таблицы
            with self.Session() as session:
                query = session.query(
                    table.c.TIMESTAMP,
                    table.c.OPEN,
                    table.c.CLOSE,
                    table.c.HIGH,
                    table.c.LOW,
                    table.c.VOLUME,
                    table.c.VOLUME_USDT
                ).all()
            # Преобразуем результат в словарь
            d = dict(
                (col, [row[i] for row in query]) for i, col in enumerate(
                    ['date', 'open', 'close', 'high', 'low', 'volume', 'volume_usdt']
                    ))
            # Добавляем ключ и значение в словарь
            data[timeframe] = d
        # Возвращаем словарь данных
        return data

    
    # Запрос на получение последних данных из биржи
    # Допили работу с сессияими нужно каким-то хуем импортировать классы которые создаёт функция
    def get_charts(
            self, Base, classes_dict,
            load_data_after = None, load_data_before = None,
            lenghts = None
            ):
        """
        Requests and stores market data from an API.

        Args:
            Base: The base class for creating classes.
            classes_dict: A dictionary containing classes.
            load_data_after: Timestamp to load data after.
            load_data_before: Timestamp to load data before.
            lengths: Number of data points to retrieve.

        Returns:
            None.
        """
        
        if load_data_before is None:
            load_data_before = ''
        if load_data_after is None:
            load_data_after = ''
        if lenghts is None:
            lenghts = ''
        marketDataAPI = MarketData.MarketAPI(self.flag)
        for instId in self.instIds:
            for timeframe in self.timeframes:
                result = marketDataAPI.get_candlesticks(
                    instId=instId,
                    after=load_data_after,
                    before=load_data_before,
                    bar=timeframe,
                    limit=lenghts # 300 Лимит Okx на 1 реквест
                )
                print(result)
                # sourcery skip: remove-zero-from-range
                for i in range(0, lenghts-1):
                    time = datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3)
                    open_ = result["data"][i][1]
                    close = result["data"][i][2]
                    high = result["data"][i][3]
                    low = result["data"][i][4]
                    volume = result["data"][i][6]
                    volume_usdt = result["data"][i][7]
                    class_name = f"ChartsData_{instId}_{timeframe}"
                    active_class = classes_dict[class_name]
                    # Проверка наличия записи с таким же TIMESTAMP
                    with self.Session() as session:
                        target_data = session.query(exists().where(active_class.TIMESTAMP == time)).scalar()
                        if not target_data:
                            data = active_class(
                                TIMESTAMP=time,
                                INSTRUMENT=instId,
                                TIMEFRAME=timeframe,
                                OPEN=open_,
                                CLOSE=close,
                                HIGH=high,
                                LOW=low,
                                VOLUME=volume,
                                VOLUME_USDT=volume_usdt
                            )
                            session.add(data)
                            #Применяем изменения
                            session.commit()


    
    @staticmethod
    def get_current_chart_data(
            flag, instId, timeframe, Base, Session, classes_dict,
            load_data_after = None, load_data_before = None,
            lenghts = None
            ):
        """
        Requests and stores current market data from an API.

        Args:
            flag: Flag for the data request.
            instId: Instrument ID for the data request.
            timeframe: Timeframe for the data request.
            Base: The base class for creating classes.
            Session: Session for database interaction.
            classes_dict: A dictionary containing classes.
            load_data_after: Timestamp to load data after.
            load_data_before: Timestamp to load data before.
            lenghts: Number of data points to retrieve.

        Returns:
            pd.DataFrame: DataFrame containing market data.
        """
        if load_data_before is None:
            load_data_before = ''
        if load_data_after is None:
            load_data_after = ''
        if lenghts is None:
            lenghts = ''
        marketDataAPI = MarketData.MarketAPI(flag)
        data_frame = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Usdt Volume'])
        result = marketDataAPI.get_candlesticks(
            instId=instId,
            after=load_data_after,
            before=load_data_before,
            bar=timeframe,
            limit=lenghts # 300 Лимит Okx на 1 реквест
        )
        lenghts = len(result["data"])
        print(result)
        data_list = []
        # Проверяем, что данные получены и список не пустой
        if 'data' in result and len(result["data"]) > 0:
            lenghts = len(result["data"])
            print(result)
            print(f'\n\n{lenghts}\n\n')
            # Итерируемся по данным и заполняем список словарей
            for i in range(lenghts):
                time = datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3)
                data_dict = {
                    'Datetime': time.strftime('%Y-%m-%d %H:%M:%S%z'),
                    'Open': float(result["data"][i][1]),
                    'High': float(result["data"][i][2]),
                    'Low': float(result["data"][i][3]),
                    'Close': float(result["data"][i][4]),
                    'Volume': float(result["data"][i][6]),
                    'Usdt Volume': float(result["data"][i][7])
                }
                data_list.append(data_dict)
            class_name = f"ChartsData_{instId}_{timeframe}"
            active_class = classes_dict[class_name]
            with Session() as session:
                # Итерируемся по строкам DataFrame
                for index, row in data_frame.iterrows():
                    # Создаем экземпляр класса модели для каждой строки
                    data = active_class(
                        TIMESTAMP=row['Datetime'],
                        INSTRUMENT=instId,
                        TIMEFRAME=timeframe,
                        OPEN=row['Open'],
                        CLOSE=row['Close'],
                        HIGH=row['High'],
                        LOW=row['Low'],
                        VOLUME=row['Volume'],
                        VOLUME_USDT=row['Usdt Volume']
                    )
                    # Проверяем, существует ли уже запись с таким же TIMESTAMP
                    target_data = session.query(exists().where(active_class.TIMESTAMP == row['Datetime'])).scalar()
                    if not target_data:
                        # Если записи нет, добавляем новый экземпляр в сессию
                        session.add(data)
                # Применяем изменения в базе данных
                session.commit()
            # Создаем DataFrame из списка словарей
            data_frame = pd.DataFrame(data_list)
            # Преобразуем типы данных
            data_frame['Datetime'] = pd.to_datetime(data_frame['Datetime'])
            data_frame['Open'] = data_frame['Open'].astype(float)
            data_frame['High'] = data_frame['High'].astype(float)
            data_frame['Low'] = data_frame['Low'].astype(float)
            data_frame['Close'] = data_frame['Close'].astype(float)
            data_frame['Volume'] = data_frame['Volume'].astype(float)
            data_frame['Usdt Volume'] = data_frame['Usdt Volume'].astype(float)
            # Выводим первые строки DataFrame для проверки
            print(data_frame.head())
        else:
            print("Данные отсутствуют или неполные")
        return data_frame
                    
                    
    """
    #Пример использования
    data_class = DataAllDatasets(instIds, flag, timeframes, Session)
    data_class.get_charts(Base, classes_dict, None, None, 300)
    """





