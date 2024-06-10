import numpy as np


class IndicatorSignals:

    @staticmethod
    def bollinger_bands_signal(data):
        """
        Generates trading signals based on the position of the closing price relative to the Bollinger Bands.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', and 'Lower Band'.

        Returns:
        - DataFrame: Data with added columns for Buy Signal and Sell Signal.
        """
        buy_signal = []
        sell_signal = []
        for i in range(len(data)):
            if data['Close'][i] < data['Lower Band'][i]:
                buy_signal.append(data['Close'][i])
                sell_signal.append(np.nan)
            elif data['Close'][i] > data['Upper Band'][i]:
                sell_signal.append(data['Close'][i])
                buy_signal.append(np.nan)
            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        data['Buy Signal'] = buy_signal
        data['Sell Signal'] = sell_signal

        return data

    @staticmethod
    def kama_signal(data):
        # Генерация сигналов покупки и продажи
        data['Signal'] = 0  # Инициализация колонки сигналов
        data.loc[data['Close'] > data['KAMA'], 'Signal'] = 1  # Сигнал на покупку
        data.loc[data['Close'] < data['KAMA'], 'Signal'] = -1  # Сигнал на продажу

        return data

    @staticmethod
    def mama_signals(data):
        # Создаем сигналы для покупки и продажи
        buy_signals = (data['MAMA'] > data['FAMA']) & (data['MAMA'].shift(1) < data['FAMA'].shift(1))
        sell_signals = (data['MAMA'] < data['FAMA']) & (data['MAMA'].shift(1) > data['FAMA'].shift(1))

        return buy_signals, sell_signals
