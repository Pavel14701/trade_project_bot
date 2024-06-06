import numpy as np
import matplotlib.pyplot as plt
# from test_data_loading import LoadDataFromYF

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
        # ... (существующий код остается без изменений) ...

        # Добавляем сигналы покупки и продажи
        data['Buy_Signal'] = np.where((data['WMAV'] > data['Close']) & (data['ADX_Strong_Trend']), 1, 0)
        data['Sell_Signal'] = np.where((data['WMAV'] < data['Close']) & (data['ADX_Strong_Trend']), -1, 0)
        return data

    @staticmethod
    def create_vizualization_vwma_adx(data):
        # ... (существующий код остается без изменений) ...

        # Добавляем сигналы на график
        plt.scatter(data.index[data['Buy_Signal'] == 1], data['Close'][data['Buy_Signal'] == 1], label='Buy', marker='^', color='green')
        plt.scatter(data.index[data['Sell_Signal'] == -1], data['Close'][data['Sell_Signal'] == -1], label='Sell', marker='v', color='red')

        # ... (остальная часть кода для визуализации) ...

# Пример использования
# data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
# print(data)
# data = VWMAbasADX.calculate_vwma_bas_adx(data, ADX_Period = 14, ADX_Threshold = 25, ADX_Smooth = 2, WMAV_lenghts = 20)
# VWMAbasADX.create_vizualization_vwma_adx(data)
