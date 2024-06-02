import matplotlib.pyplot as plt
import talib
#from test_data_loading import LoadDataFromYF

class MesaAdaptiveMA:
    """Summary:
    Class for calculating and plotting the MESA Adaptive Moving Average (MAMA) and FAMA.

    Explanation:
    This class provides static methods to calculate MAMA and FAMA values based on High and Low prices, generate buy and sell signals, and plot the MAMA and FAMA along with buy and sell signals on a price chart.

    Args:
    - data: The input data containing High and Low prices.

    Returns:
    - For calculate_mama: A tuple containing MAMA values, FAMA values, input data, buy signals, and sell signals.
    - For plot_mama: None
    """
    
    
    @staticmethod
    def calculate_mama(data):
        """Summary:
        Calculate MESA Adaptive Moving Average (MAMA) and signals.

        Explanation:
        This static method calculates the MAMA and FAMA values based on the average of High and Low prices, generates buy and sell signals, and returns the calculated values and signals.

        Args:
        - data: The input data containing High and Low prices.

        Returns:
        - Tuple containing MAMA values, FAMA values, input data, buy signals, and sell signals.
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
        Plot the MESA Adaptive Moving Average (MAMA) and FAMA.

        Explanation:
        This static method visualizes the Close Price along with the MAMA and FAMA values, highlighting buy and sell signals on the price chart.

        Args:
        - mama: The MAMA values.
        - fama: The FAMA values.
        - data: The input data containing Close prices.
        - buy_signals: Boolean array indicating buy signals.
        - sell_signals: Boolean array indicating sell signals.

        Returns:
        None
        """
        # Визуализируем данные
        plt.figure(figsize=(10, 5))
        plt.plot(data['Close'], label='Close Price')
        plt.plot(mama, label='MAMA', color='red')
        plt.plot(fama, label='FAMA', color='green')
        # Добавляем сигналы на график
        plt.plot(data.index[buy_signals], data['Close'][buy_signals], '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(data.index[sell_signals], data['Close'][sell_signals], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.title('MESA Adaptive Moving Average (MAMA) and FAMA')
        plt.legend()
        plt.show()

"""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
mama, fama, data, buy_signals, sell_signals= MesaAdaptiveMA.calculate_mama(data)
MesaAdaptiveMA.plot_mama(mama, fama, data, buy_signals, sell_signals)
"""