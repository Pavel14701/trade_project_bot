import matplotlib.pyplot as plt
import talib
#from test_data_loading import LoadDataFromYF


class BollindgerBands:
    """
    A class for calculating and visualizing Bollinger Bands on stock price data.

    Methods:
    - calculate_bands(data, lenghts, stdev): Calculates Bollinger Bands based on the given data, lengths, and standard deviations.
    - create_vizualization_bb(data): Creates a visualization of stock price with Bollinger Bands.
    """
    
    @staticmethod
    def calculate_bands(data, lenghts, stdev):
        """
        Calculates Bollinger Bands based on the given data, lengths, and standard deviations.

        Args:
        - data (DataFrame): Input data containing 'High' and 'Low' prices.
        - lenghts (int): Length of the moving average window.
        - stdev (int): Standard deviation multiplier for the bands.

        Returns:
        - DataFrame: Data with added columns for Upper Band, Middle Band, and Lower Band.
        """
        # Рассчитываем среднее значение между максимальной и минимальной ценой для каждого периода
        high_low_average = (data['High'] + data['Low']) / 2
        # Рассчитываем полосы Боллинджера на основе среднего значения между High и Low
        upper_band, middle_band, lower_band = talib.BBANDS(
            high_low_average,
            timeperiod=lenghts, # Defolt 20
            nbdevup=stdev, # cтандарт 2
            nbdevdn=stdev, # стандарт 2 не знаю нахуя тут два пункта
            matype=0 # тип скользящей 
        )
        # Добавляем результаты в DataFrame
        data['Upper Band'] = upper_band
        data['Middle Band'] = middle_band
        data['Lower Band'] = lower_band
        return data


    @staticmethod
    def create_vizualization_bb(data):
        """
        Creates a visualization of stock price with Bollinger Bands.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', and 'Lower Band' values.

        Returns:
        None
        """
        fig, ax = plt.subplots(figsize=(14, 7))  # Исправление здесь
        ax.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax.plot(data.index, data['Upper Band'], label='Верхняя полоса', color='red', linestyle='--')
        ax.plot(data.index, data['Middle Band'], label='Средняя полоса', color='black', linestyle='-.')
        ax.plot(data.index, data['Lower Band'], label='Нижняя полоса', color='green', linestyle='--')
        ax.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='grey', alpha=0.1)
        ax.legend()
        ax.set_title('Визуализация полос Боллинджера')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()

""""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = BollindgerBands.calculate_bands(data, lenghts=34, stdev=2)
print(data)
BollindgerBands.create_vizualization_bb(data)
"""
