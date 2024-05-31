import numpy as np
import matplotlib.pyplot as plt
#from test_data_loading import LoadDataFromYF


class VWMAbasADX:
    @staticmethod
    def calculate_vwma_bas_adx(data, ADX_Period, ADX_Threshold, ADX_Smooth, WMAV_lenghts):
        # Вычисляем +DI и -DI с периодом 14
        DI_Period = 14
        data["UpMove"] = data["High"].diff()
        data["DownMove"] = data["Low"].diff()
        data["+DM"] = np.where((data["UpMove"] > data["DownMove"]) & (data["UpMove"] > 0), data["UpMove"], 0)
        data["-DM"] = np.where((data["DownMove"] > data["UpMove"]) & (data["DownMove"] > 0), data["DownMove"], 0)
        data["+DM_Smooth"] = data["+DM"].ewm(span=DI_Period, adjust=False).mean()
        data["-DM_Smooth"] = data["-DM"].ewm(span=DI_Period, adjust=False).mean()
        data["ATR"] = data["Close"].diff().abs().ewm(span=DI_Period, adjust=False).mean()
        data["+DI"] = data["+DM_Smooth"] / data["ATR"] * 100
        data["-DI"] = data["-DM_Smooth"] / data["ATR"] * 100
        """
        #Стандартные настройки ADX
        # Вычисляем ADX c периодом 14, порогом 25 и сглаживанием
        ADX_Period = 14
        ADX_Threshold = 25 #Подсвечивает сильный тренд
        ADX_Smooth = 2
        """
        # Вычисляем ADX и сглаживаем его
        data["DX"] = np.abs(data["+DI"] - data["-DI"]) / (data["+DI"] + data["-DI"]) * 100
        data["ADX"] = data["DX"].ewm(span=ADX_Period, adjust=False).mean()
        data["ADX_Smooth"] = data["ADX"].ewm(span=ADX_Smooth, adjust=False).mean()
        # Добавляем логику порогового значения
        data["ADX_Strong_Trend"] = data["ADX_Smooth"] > ADX_Threshold
        # Находим локальные максимумы и минимумы линии ADX
        data["ADX_Peak"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) < data["ADX_Smooth"]) & (data["ADX_Smooth"].shift(-1) < data["ADX_Smooth"])).ffill(limit=1)
        data["ADX_Trough"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) > data["ADX_Smooth"]) & (data["ADX_Smooth"].shift(-1) > data["ADX_Smooth"])).ffill(limit=1)
        # Соединяем эти точки с помощью линии тренда ADX
        data["ADX_Trend"] = np.nan
        data.loc[data["ADX_Peak"].notna(), "ADX_Trend"] = data["ADX_Peak"]
        data.loc[data["ADX_Trough"].notna(), "ADX_Trend"] = data["ADX_Trough"]
        data["ADX_Trend"] = data["ADX_Trend"].interpolate(method="linear")
        # Создаем пустой список для хранения значений WMAV
        WMAV = []
        # Задаем период скользящей средней
        n = 20
        # Проходим по данным с шагом 1 час, начиная с n-го часа
        for i in range(n, len(data)):
            # Выбираем данные за последние n часов
            data_n = data.iloc[i-WMAV_lenghts:i]
            # Вычисляем числитель и знаменатель формулы WMAV
            numerator = (data_n["Volume"] * data_n["Close"] * data_n["ADX_Trend"]).sum()
            denominator = (data_n["Volume"] * data_n["ADX_Trend"]).sum()
            # Вычисляем значение WMAV и добавляем его в список
            WMAV.append(numerator / (denominator + 1e-9))
        # Добавляем значения WMAV в исходный датафрейм
        data["WMAV"] = np.nan
        data.loc[data.index[WMAV_lenghts:], "WMAV"] = WMAV
        return data


    @staticmethod
    def create_vizualization_vwma_adx(data):
        plt.figure(figsize=(10, 6))
        # Строим график цены
        plt.plot(data.index, data["Close"], label="Price", color='black')
        # Строим график VWMA с изменением цвета в зависимости от силы тренда
        plt.plot(data.index, data["WMAV"], label="WMAV", color='grey')
        plt.plot(data.index[data["ADX_Strong_Trend"]], data["WMAV"][data["ADX_Strong_Trend"]], label="Strong Trend", color='red')
        plt.title("Apple Stock Price with WMAV and ADX Trendline")
        plt.xlabel("Date")
        plt.ylabel("USD")
        plt.legend()
        plt.show()

""""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = VWMAbasADX.calculate_vwma_bas_adx(data, ADX_Period = 14, ADX_Threshold = 25, ADX_Smooth = 2, WMAV_lenghts = 20)
VWMAbasADX.create_vizualization_vwma_adx(data)
"""
