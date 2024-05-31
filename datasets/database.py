from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from datetime import datetime, timedelta


class DataAllDatasets:
    def __init__(self, instIds, timeframes, Session=None):
        self.instIds = instIds
        self.timeframes = timeframes
        self.Session = Session


    # Функция для создания классов с заданными параметрами
    def create_classes(self, Base):
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
    def get_bd_marketdata(self, classes, timeframe, instId):
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
            d = dict((col, [row[i] for row in query]) for i, col in enumerate(['date', 'open', 'close', 'high', 'low', 'volume', 'volume_usdt']))
            # Добавляем ключ и значение в словарь
            data[timeframe] = d
        # Возвращаем словарь данных
        return data

    
    # Запрос на получение последних данных из биржи
    # Допили работу с сессияими нужно каким-то хуем импортировать классы которые создаёт функция
    def get_charts(self, marketDataAPI, Base, load_data_after = None, load_data_before = None, lenghts = None):
        for timeframe in self.timeframes:
            result = marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=load_data_after,
                before=load_data_before,
                bar=timeframe,
                limit=lenghts # 300 Лимит Okx на 1 реквест
            )
            print(result)
            for i in range(0, 299):
                time = datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3)
                open = result["data"][i][1]
                close = result["data"][i][2]
                high = result["data"][i][3]
                low = result["data"][i][4]
                volume = result["data"][i][6]
                volume_usdt = result["data"][i][7]
                '''
                Вот эту хуету с созданием класса на лету 
                будешь сам дебажить, костыльно пиздец вышло
                '''
                class_name = f"ChartsData_{self.inst_id}_{timeframe}"
                # Создаем новый класс с помощью type()
                ClassKostyl = type(class_name, (Base,), {})
                data = ClassKostyl(
                    TIMESTAMP=time,
                    INSTRUMENT=self.instId,
                    TIMEFRAME=timeframe,
                    OPEN=open,
                    CLOSE=close,
                    HIGH=high,
                    LOW=low,
                    VOLUME=volume,
                    VOLUME_USDT=volume_usdt
                )
                with self.Session() as session:
                    session.add(data)
                    #Применяем изменения
                    session.commit()









