import matplotlib.pyplot as plt
import yfinance as yf
import talib
import numpy as np

# Загружаем данные по акциям Apple
data = yf.download("AAPL", start="2022-06-14", end="2024-02-14", interval="1h")

# Рассчитываем среднее значение между максимальной и минимальной ценой для каждого периода
high_low_average = (data['High'] + data['Low']) / 2

# Рассчитываем полосы Боллинджера на основе среднего значения между High и Low
upper_band, middle_band, lower_band = talib.BBANDS(
    high_low_average,
    timeperiod=20,
    nbdevup=2,
    nbdevdn=2,
    matype=0
)

# Добавляем результаты в DataFrame
data['Upper Band'] = upper_band
data['Middle Band'] = middle_band
data['Lower Band'] = lower_band

# Выводим результаты
print(data[['High', 'Low', 'Upper Band', 'Middle Band', 'Lower Band']])


# Построение графика цены закрытия актива
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Close'], label='Цена закрытия', color='blue')

# Построение графика верхней полосы Боллинджера
plt.plot(data.index, data['Upper Band'], label='Верхняя полоса Боллинджера', color='red', linestyle='--')

# Построение графика средней полосы Боллинджера
plt.plot(data.index, data['Middle Band'], label='Средняя полоса Боллинджера', color='green', linestyle='--')

# Построение графика нижней полосы Боллинджера
plt.plot(data.index, data['Lower Band'], label='Нижняя полоса Боллинджера', color='red', linestyle='--')

# Настройка заголовка и легенды
plt.title('График цены закрытия и полос Боллинджера для AAPL')
plt.legend()

# Отображение графика
plt.show()
