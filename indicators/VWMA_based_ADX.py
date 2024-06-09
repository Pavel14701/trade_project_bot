import numpy as np

from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer


class VWMAbasADX:
    """Summary:
    Class for calculating and visualizing VWMA-based ADX.

    Explanation:
    This class provides static methods to calculate the VWMA-based ADX values, including ADX trend analysis and visualization of VWMA and ADX trendline based on the provided data.

    Args:
    - data: The input data containing price, volume, and ADX values.
    - ADX_Period: The period for ADX calculation.
    - ADX_Threshold: The threshold value for identifying a strong trend.
    - ADX_Smooth: The smoothing period for ADX.
    - WMAV_lenghts: The lengths for calculating WMAV.

    Returns:
    - For calculate_vwma_bas_adx: DataFrame with calculated ADX values, trend analysis, and WMAV.
    - For create_vizualization_vwma_adx: None
    """

    @staticmethod
    def calculate_vwma_bas_adx(data, ADX_Period, ADX_Threshold, ADX_Smooth, WMAV_lenghts):
        """Summary:
        Calculate VWMA-based ADX values.

        Explanation:
        This static method calculates the VWMA-based ADX values, including trend analysis and WMAV calculation, based on the provided data and parameters.

        Args:
        - data: The input data containing price, volume, and ADX values.
        - ADX_Period: The period for ADX calculation. Defolt 14
        - ADX_Threshold: The threshold value for identifying a strong trend. Defolt 25
        - ADX_Smooth: The smoothing period for ADX. Defolt 2
        - WMAV_lenghts: The lengths for calculating WMAV.

        Returns:
        - DataFrame with calculated ADX values, trend analysis, and WMAV.
        """
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
        # Вычисляем ADX и сглаживаем его
        data["DX"] = np.abs(data["+DI"] - data["-DI"]) / (data["+DI"] + data["-DI"]) * 100
        data["ADX"] = data["DX"].ewm(span=ADX_Period, adjust=False).mean()
        data["ADX_Smooth"] = data["ADX"].ewm(span=ADX_Smooth, adjust=False).mean()
        # Добавляем логику порогового значения
        data["ADX_Strong_Trend"] = data["ADX_Smooth"] > ADX_Threshold
        # Находим локальные максимумы и минимумы линии ADX
        data["ADX_Peak"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) < data["ADX_Smooth"]) & (
                    data["ADX_Smooth"].shift(-1) < data["ADX_Smooth"])).ffill(limit=1)
        data["ADX_Trough"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) > data["ADX_Smooth"]) & (
                    data["ADX_Smooth"].shift(-1) > data["ADX_Smooth"])).ffill(limit=1)
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
            data_n = data.iloc[i - WMAV_lenghts:i]
            # Вычисляем числитель и знаменатель формулы WMAV
            numerator = (data_n["Volume"] * data_n["Close"] * data_n["ADX_Trend"]).sum()
            denominator = (data_n["Volume"] * data_n["ADX_Trend"]).sum()
            # Вычисляем значение WMAV и добавляем его в список
            WMAV.append(numerator / (denominator + 1e-9))
        # Добавляем значения WMAV в исходный датафрейм
        data["WMAV"] = np.nan
        data.loc[data.index[WMAV_lenghts:], "WMAV"] = WMAV
        # Добавляем сигналы покупки и продажи
        data['Buy_Signal'] = np.where((data['WMAV'] > data['Close']) & (data['ADX_Strong_Trend']), 1, 0)
        data['Sell_Signal'] = np.where((data['WMAV'] < data['Close']) & (data['ADX_Strong_Trend']), -1, 0)
        return data


# Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = VWMAbasADX.calculate_vwma_bas_adx(data, ADX_Period=14, ADX_Threshold=25, ADX_Smooth=2, WMAV_lenghts=20)
IndicatorDrawer.draw_vwma_based_adx(data)
