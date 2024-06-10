import matplotlib.pyplot as plt
import talib


# Здесь должен быть ваш код для загрузки данных, например из Yahoo Finance
from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer

class MesaAdaptiveMA:
    """Summary:
    Класс для расчета и построения MESA Adaptive Moving Average (MAMA) и FAMA.

    Explanation:
    Этот класс предоставляет статические методы для расчета значений MAMA и FAMA на основе цен High и Low, генерации сигналов покупки и продажи, и построения MAMA и FAMA вместе с сигналами покупки и продажи на графике цен.

    Args:
    - data: Входные данные, содержащие цены High и Low.

    Returns:
    - Для calculate_mama: Кортеж, содержащий значения MAMA, значения FAMA, входные данные, сигналы покупки и сигналы продажи.
    - Для plot_mama: None
    """

    @staticmethod
    def calculate_mama(data):
        """Summary:
        Расчет MESA Adaptive Moving Average (MAMA) и сигналов.

        Explanation:
        Этот статический метод рассчитывает значения MAMA и FAMA на основе среднего значения цен High и Low, генерирует сигналы покупки и продажи, и возвращает рассчитанные значения и сигналы.

        Args:
        - data: Входные данные, содержащие цены High и Low.

        Returns:
        - Кортеж, содержащий значения MAMA, значения FAMA, входные данные, сигналы покупки и сигналы продажи.
        """
        # Вычисляем среднее значение между High и Low для каждого дня
        mid_prices = (data['High'] + data['Low']) / 2
        # Вычисляем MAMA и FAMA, используя средние цены
        mama, fama = talib.MAMA(mid_prices, fastlimit=0.5, slowlimit=0.05)
        data['MAMA'] = mama
        data['FAMA'] = fama

        return data



#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")

print(data)
mama, fama, data, buy_signals, sell_signals = MesaAdaptiveMA.calculate_mama(data)
IndicatorDrawer.draw_mama(mama, fama, data, buy_signals, sell_signals)