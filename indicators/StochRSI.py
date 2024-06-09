import talib
import pandas as pd

from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer


class StochRSICalculator:
    """Summary:
    Class for calculating and visualizing Stochastic RSI (StochRSI).

    Explanation:
    This class provides static methods to calculate StochRSI values, including Fast %K and Fast %D lines, and visualize the StochRSI indicator with buy and sell signals based on the provided data.

    Args:
    - data: The input data containing Close prices.

    Returns:
    - For calculate_stochrsi: Tuple containing input data, Fast %D values, and Fast %K values.
    - For plot_stochrsi: None
    """

    @staticmethod
    def calculate_stochrsi(data):
        """Summary:
        Calculate Stochastic RSI (StochRSI) values.

        Explanation:
        This static method calculates the Stochastic RSI (StochRSI) values based on the Close prices in the provided data.

        Args:
        - data: The input data containing Close prices.

        Returns:
        - Tuple containing the input data, Fast %D values, and Fast %K values.
        """
        # Рассчитываем StochRSI
        fastk, fastd = talib.STOCHRSI(data['Close'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        # Преобразуем numpy массивы в pandas Series с правильным индексом
        fastk = pd.Series(fastk, index=data.index)
        fastd = pd.Series(fastd, index=data.index)
        return (data, fastd, fastk)


# Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data, fastd, fastk = StochRSICalculator.calculate_stochrsi(data)
IndicatorDrawer.draw_stochRsi(fastk, fastd, data)


