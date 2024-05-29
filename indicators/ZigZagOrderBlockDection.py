# Импортируем необходимые библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import yfinance as yf

# Задаем параметры индикатора
percent_change = 0.003036 # Порог изменения цены в процентах

# Считываем данные цен из файла или источника
# Загружаем данные по акциям Apple
df = yf.download("BTC", start="2023-01-01", end="2024-02-14", interval="1D")
print(df)
data_x = df.index.values # Массив индексов
data_high = df["High"].values # Массив цен high
data_low = df["Low"].values # Массив цен low

# Находим пики (максимумы) по high
peak_indexes = signal.argrelextrema(data_high, np.greater)
peak_indexes = peak_indexes[0]

# Находим впадины (минимумы) по low
valley_indexes = signal.argrelextrema(data_low, np.less)
valley_indexes = valley_indexes[0]

# Объединяем пики и впадины в один датафрейм
df_peaks = pd.DataFrame({"date": data_x[peak_indexes], "zigzag_y": data_high[peak_indexes], "type": "high"})
df_valleys = pd.DataFrame({"date": data_x[valley_indexes], "zigzag_y": data_low[valley_indexes], "type": "low"})
df_peaks_valleys = pd.concat([df_peaks, df_valleys], axis=0, ignore_index=True, sort=True)

# Сортируем датафрейм по дате
df_peaks_valleys = df_peaks_valleys.sort_values(by=["date"])

# Удаляем лишние пики и впадины, которые не чередуются
mask = [True]
previous_type = df_peaks_valleys.iloc[0]["type"]
for i in range(1, len(df_peaks_valleys)):
    current_type = df_peaks_valleys.iloc[i]["type"]
    if current_type != previous_type:
        previous_type = current_type
        mask.append(True)
    else:
        mask.append(False)
df_peaks_valleys = df_peaks_valleys[mask]

# Фильтруем датафрейм по порогу изменения цены
previous_high = df_peaks_valleys.iloc[0]["zigzag_y"]
previous_low = df_peaks_valleys.iloc[0]["zigzag_y"]
mask = [True]
for i in range(1, len(df_peaks_valleys)):
    value = df_peaks_valleys.iloc[i]["zigzag_y"]
    type = df_peaks_valleys.iloc[i]["type"]
    if type == "High":
        relative_difference = np.abs(value - previous_high) / previous_high
        if relative_difference > percent_change:
            previous_high = value
            mask.append(True)
        else:
            mask.append(False)
    else:
        relative_difference = np.abs(value - previous_low) / previous_low
        if relative_difference > percent_change:
            previous_low = value
            mask.append(True)
        else:
            mask.append(False)
filtered = df_peaks_valleys[mask]

# Рисуем график с индикатором зиг-заг
plt.figure(figsize=(10, 10))
plt.plot(df_peaks_valleys["date"].values, df_peaks_valleys["zigzag_y"].values, color="red", label="Extrema")
plt.plot(filtered["date"].values, filtered["zigzag_y"].values, color="blue", label="ZigZag")
plt.plot(data_x, data_high, linestyle="dashed", color="black", label="High line", linewidth=1)
plt.plot(data_x, data_low, linestyle="dashed", color="black", label="Low line", linewidth=1)

# Добавляем горизонтальные отрезки для каждой точки ZigZag
for i in range(len(filtered)):
    # get the date and zigzag_y value of the point
    date = filtered.iloc[i]["date"]
    y = filtered.iloc[i]["zigzag_y"]

    # get the high and low values of the corresponding row in df
    high = df.loc[date, "High"]
    low = df.loc[date, "Low"]

    # draw horizontal lines at high and low levels
    plt.hlines(y=high, xmin=date, xmax=date + pd.Timedelta(days=30), color="green", linestyle=":", linewidth=1)
    plt.hlines(y=low, xmin=date, xmax=date + pd.Timedelta(days=30), color="red", linestyle=":", linewidth=1)

plt.legend()
plt.show()
