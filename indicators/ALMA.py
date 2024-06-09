import numpy as np

from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer


class AlmaIndicator:

    @staticmethod
    def calculate_alma(data, lenghts):
        """
        Calculate ALMA indicator based on the given data and lengths.

        Args:
            data: Pandas DataFrame containing stock price data.
            lenghts: Integer representing the length of the window for ALMA calculation.

        Returns:
            Pandas DataFrame with ALMA values added as a new column.
        """
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (lenghts - 1) / 2
        sigma = lenghts / 6
        w = np.exp(-(np.arange(lenghts) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA"] = data["Close"].rolling(lenghts).apply(lambda x: np.dot(x, w), raw=True)
        return data

    @staticmethod
    def calculate_alma_ribbon(data, lenghtsVSlow, lenghtsSlow, lenghtsMiddle, lenghtsFast, lenghtsVFast):
        """
        Calculates multiple ALMA indicators based on different lengths for the given data.

        Args:
        - data (DataFrame): Input data containing 'Close' prices.
        - lenghtsVSlow (int): Length for ALMA_VSLOW calculation.
        - lenghtsSlow (int): Length for ALMA_SLOW calculation.
        - lenghtsMiddle (int): Length for ALMA_MIDDLE calculation.
        - lenghtsFast (int): Length for ALMA_FAST calculation.
        - lenghtsVFast (int): Length for ALMA_VFAST calculation.

        Returns:
        - DataFrame: Data with added columns for ALMA_VSLOW, ALMA_SLOW, ALMA_MIDDLE, ALMA_FAST, and ALMA_VFAST.
        """
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (lenghtsVSlow - 1) / 2
        sigma = lenghtsVSlow / 6
        w = np.exp(-(np.arange(lenghtsVSlow) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA_VSLOW"] = data["Close"].rolling(lenghtsVSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsSlow - 1) / 2
        sigma = lenghtsSlow / 6
        w = np.exp(-(np.arange(lenghtsSlow) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA_SLOW"] = data["Close"].rolling(lenghtsSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsMiddle - 1) / 2
        sigma = lenghtsMiddle / 6
        w = np.exp(-(np.arange(lenghtsMiddle) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA_MIDDLE"] = data["Close"].rolling(lenghtsMiddle).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsFast - 1) / 2
        sigma = lenghtsFast / 6
        w = np.exp(-(np.arange(lenghtsFast) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA_FAST"] = data["Close"].rolling(lenghtsFast).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsVFast - 1) / 2
        sigma = lenghtsVFast / 6
        w = np.exp(-(np.arange(lenghtsVFast) - m) ** 2 / (2 * sigma ** 2))
        w = w / w.sum()
        data["ALMA_VFAST"] = data["Close"].rolling(lenghtsVFast).apply(lambda x: np.dot(x, w), raw=True)
        return data


# пример применения
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = AlmaIndicator.calculate_alma_ribbon(data, lenghtsVSlow=144, lenghtsSlow=89, lenghtsMiddle=55, lenghtsFast=34,
                                           lenghtsVFast=21)
IndicatorDrawer.draw_alma_ribbon(data)
