import yfinance as yf
import pandas as pd
import talib
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.widgets import Cursor

# Загружаем данные по акциям Apple
df = yf.download("AAPL", start="2023-01-01", end="2024-05-23", interval="1h")

# Параметры для индикаторов RSI и EMA
rsi_period_short = 7  # Короткий период для RSI
rsi_period_long = 14  # Длинный период для RSI
ema_period = 9        # Период для EMA

# Вычисляем RSI для двух периодов
rsi_short = talib.RSI(df['Close'].values, timeperiod=rsi_period_short)
rsi_long = talib.RSI(df['Close'].values, timeperiod=rsi_period_long)

# Сглаживаем RSI с помощью EMA
rsi_short_ema = talib.EMA(rsi_short, timeperiod=ema_period)
rsi_long_ema = talib.EMA(rsi_long, timeperiod=ema_period)

# Добавляем индикаторы в DataFrame
df['RSI_Short_EMA'] = rsi_short_ema
df['RSI_Long_EMA'] = rsi_long_ema

# Сигналы перекупленности и перепроданности
overbought = 70
oversold = 30

# Сигналы пересечения
cross_up = (df['RSI_Short_EMA'] > df['RSI_Long_EMA']) & (df['RSI_Short_EMA'].shift(1) <= df['RSI_Long_EMA'].shift(1))
cross_down = (df['RSI_Short_EMA'] < df['RSI_Long_EMA']) & (df['RSI_Short_EMA'].shift(1) >= df['RSI_Long_EMA'].shift(1))

# Добавляем сигналы в DataFrame
df['Cross_Up'] = cross_up
df['Cross_Down'] = cross_down

# Создаем фигуру и оси
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Строим график цены актива на первом подграфике
ax1.plot(df.index, df['Close'], label='AAPL Close Price', color='black')
ax1.set_title('AAPL Stock Price')
ax1.set_ylabel('Price', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.legend(loc='upper left')

# Строим график индикаторов RSI Cloud на втором подграфике
ax2.plot(df.index, df['RSI_Short_EMA'], label='RSI Short EMA (7)', color='blue')
ax2.plot(df.index, df['RSI_Long_EMA'], label='RSI Long EMA (14)', color='orange')
ax2.scatter(df.index[df['Cross_Up']], df['RSI_Short_EMA'][df['Cross_Up']], color='green', label='Cross Up', marker='^', alpha=1)
ax2.scatter(df.index[df['Cross_Down']], df['RSI_Short_EMA'][df['Cross_Down']], color='red', label='Cross Down', marker='v', alpha=1)
ax2.axhline(y=overbought, color='darkred', linestyle='--', label='Overbought (70)')
ax2.axhline(y=oversold, color='darkgreen', linestyle='--', label='Oversold (30)')
ax2.set_title('RSI Cloud Indicator with Signals')
ax2.set_xlabel('Date')
ax2.set_ylabel('RSI Value', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')
ax2.legend(loc='upper right')

# Создаем перекрестие, которое будет отображаться на обоих подграфиках
cursor = Cursor(ax1, useblit=True, color='gray', linewidth=1, linestyle='--')
cursor2 = Cursor(ax2, useblit=True, color='gray', linewidth=1, linestyle='--')

# Добавляем всплывающее окошко с данными
mplcursors.cursor(hover=True)

plt.tight_layout()  # Автоматически корректирует подписи, чтобы они не перекрывались
plt.show()
