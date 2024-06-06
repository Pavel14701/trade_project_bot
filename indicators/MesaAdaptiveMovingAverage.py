import matplotlib.pyplot as plt
import talib


# Здесь должен быть ваш код для загрузки данных, например из Yahoo Finance
# from test_data_loading import LoadDataFromYF

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
        # Создаем сигналы для покупки и продажи
        buy_signals = (mama > fama) & (mama.shift(1) < fama.shift(1))
        sell_signals = (mama < fama) & (mama.shift(1) > fama.shift(1))
        return (mama, fama, data, buy_signals, sell_signals)

    @staticmethod
    def plot_mama(mama, fama, data, buy_signals, sell_signals):
        """Summary:
        Построение MESA Adaptive Moving Average (MAMA) и FAMA.

        Explanation:
        Этот статический метод визуализирует цену закрытия вместе с значениями MAMA и FAMA, выделяя сигналы покупки и продажи на графике цен.

        Args:
        - mama: Значения MAMA.
        - fama: Значения FAMA.
        - data: Входные данные, содержащие цены закрытия.
        - buy_signals: Булевый массив, указывающий сигналы покупки.
        - sell_signals: Булевый массив, указывающий сигналы продажи.

        Returns:
        None
        """
        # Визуализируем данные
        plt.figure(figsize=(10, 5))
        plt.plot(data['Close'], label='Цена закрытия')
        plt.plot(mama, label='MAMA', color='red')
        plt.plot(fama, label='FAMA', color='green')
        # Добавляем сигналы на график
        plt.plot(data.index[buy_signals], data['Close'][buy_signals], '^', markersize=10, color='g', lw=0,
                 label='Сигнал покупки')
        plt.plot(data.index[sell_signals], data['Close'][sell_signals], 'v', markersize=10, color='r', lw=0,
                 label='Сигнал продажи')
        plt.title('MESA Adaptive Moving Average (MAMA) и FAMA')
        plt.legend()
        plt.show()

# Пример использования
# data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
# print(data)
# mama, fama, data, buy_signals, sell_signals = MesaAdaptiveMA.calculate_mama(data)
# MesaAdaptiveMA.plot_mama(mama, fama, data, buy_signals, sell_signals)
