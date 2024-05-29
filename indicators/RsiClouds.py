import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Загружаем данные по акциям Apple
df = yf.download("AAPL", start="2023-01-01", end="2024-05-23", interval="1h")


# Рассчитываем RSI по формуле
import pandas as pd

def rsi(data, n=34, smooth_n=5):
    delta = data['Close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(span=n, adjust=True).mean()
    ma_down = down.ewm(span=n, adjust=True).mean()
    rsi = 100 - (100 / (1 + ma_up / ma_down))
    smoothed_rsi = rsi.ewm(span=smooth_n, adjust=True).mean()
    return rsi



# Добавляем колонку RSI к датафрейму
df['RSI'] = rsi(df)


# Рассчитываем EMA от RSI по формуле
def ema_rsi(data, n):
    return data.ewm(span=n, adjust=False).mean()


# Добавляем колонки EMA от RSI к датафрейму
df['EMA_RSI_9'] = ema_rsi(df['RSI'], 5)
df['EMA_RSI_26'] = ema_rsi(df['RSI'], 34)

df['EMA_RSI_9'] = ema_rsi(df['RSI'], 14)  # Было 5, стало 14
df['EMA_RSI_26'] = ema_rsi(df['RSI'], 50)  # Было 34, стало 50

# Применяем дополнительное скользящее среднее к EMA_RSI
df['SMA_of_EMA_RSI_9'] = df['EMA_RSI_9'].rolling(window=5).mean()
df['SMA_of_EMA_RSI_26'] = df['EMA_RSI_26'].rolling(window=5).mean()


# Рассчитываем сигналы по точкам пересечения EMA от RSI
def crossover_signal(data):
    diff = np.diff(np.sign(data['EMA_RSI_9'] - data['EMA_RSI_26']))
    buy = np.where(diff == 2)[0] + 1
    sell = np.where(diff == -2)[0] + 1
    return buy, sell


# Добавляем колонки сигналов к датафрейму
df['Buy'] = np.nan
df['Sell'] = np.nan
buy, sell = crossover_signal(df)
# Используем iloc и списки для выбора строк по позициям
df.iloc[list(buy), df.columns.get_loc('Buy')] = df.iloc[list(buy), df.columns.get_loc('Close')]
df.iloc[list(sell), df.columns.get_loc('Sell')] = df.iloc[list(sell), df.columns.get_loc('Close')]

# Строим графики индикаторов
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df['RSI'], label='RSI')
ax.plot(df['EMA_RSI_9'], label='EMA RSI 9')
ax.plot(df['EMA_RSI_26'], label='EMA RSI 26')
ax.axhline(70, color='r', linestyle='--')
ax.axhline(30, color='g', linestyle='--')
ax.legend()
ax.set_title('RSI и EMA от него')

# Добавляем область заливки между EMA от RSI
ax.fill_between(df.index, df['EMA_RSI_9'], df['EMA_RSI_26'],
                where=df['EMA_RSI_9'] > df['EMA_RSI_26'], facecolor='green', alpha=0.5)
ax.fill_between(df.index, df['EMA_RSI_9'], df['EMA_RSI_26'],
                where=df['EMA_RSI_9'] < df['EMA_RSI_26'], facecolor='red', alpha=0.5)

# Добавляем точки покупки и продажи
ax.plot(df['Close'], label='Цена закрытия')
ax.scatter(df.index, df['Buy'], marker='^', color='green', label='Buy')
ax.scatter(df.index, df['Sell'], marker='v', color='red', label='Sell')
ax.legend()
plt.tight_layout()
plt.show()
