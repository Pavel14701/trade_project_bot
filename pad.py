import pandas as pd
from datetime import datetime
from okx import MarketData



# Создайте объект MarketData API
marketOperator = MarketData.MarketAPI(flag='0')

# Определите параметры получения данных
symbol = "BTC-USDT"  # Торговая пара (например, BTC-USDT, ETH-USDT)
bar_interval = "15m"  # Интервал времени (например, 1m, 5m, 15m, 1h, 4h, 24h)

# Инициализируйте пустой DataFrame
timestamp = 0
columns = ['Open', 'High', 'Low', 'Close']  # Настройте столбцы по своему усмотрению
dataframe = pd.DataFrame(columns=columns)

# Итеративно получайте и добавляйте данные
for _ in range(10):
    data = marketOperator.get_mark_price_candlesticks(symbol, after=, bar='15m')
    timestamp = int(data.get('data')[0][0])
    dataframe = pd.concat([dataframe, pd.DataFrame(data['data'], columns=columns)], ignore_index=True)

# Преобразуйте метки времени в объекты datetime
indexlist = dataframe['Timestamp'].copy()
for i, elem in enumerate(indexlist):
    indexlist[i] = datetime.fromtimestamp(int(elem) // 1000)  # Используйте целочисленное деление для миллисекунд
dataframe.index = indexlist

# Удалите ненужные столбцы
dataframe = dataframe.drop(['Timestamp'], axis=1)

# Отобразите обработанный DataFrame
print(dataframe)
