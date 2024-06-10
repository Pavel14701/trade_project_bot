import matplotlib.pyplot as plt
import mplcursors


class IndicatorDrawer:
    @staticmethod
    def draw_stochrsi(fastk, fastd, data):
        """Summary:
        Plot Stochastic RSI (StochRSI) with buy and sell signals.

        Explanation:
        This static method visualizes the Stochastic RSI (StochRSI) indicator with Fast %K and Fast %D lines, highlighting buy and sell signals based on the provided data.

        Args:
        - fastk: The Fast %K line values.
        - fastd: The Fast %D line values.
        - data: The input data containing Close prices.

        Returns:
        None
        """
        # Стандартные сигналы для StochRSI
        buy_signals = (fastk > fastd) & (fastk.shift(1) < fastd.shift(1)) & (fastk < 20)
        sell_signals = (fastk < fastd) & (fastk.shift(1) > fastd.shift(1)) & (fastk > 80)
        # Визуализация
        plt.figure(figsize=(14, 7))
        plt.subplot(2, 1, 1)
        plt.plot(data['Close'], label='Цена закрытия')
        plt.title('Цена закрытия')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(fastk, label='Fast %K line', color='blue')
        plt.plot(fastd, label='Fast %D line', color='orange')
        plt.fill_between(data.index, fastk, fastd, where=fastk > fastd, color='lightgreen', alpha=0.5)
        plt.fill_between(data.index, fastk, fastd, where=fastk < fastd, color='lightcoral', alpha=0.5)
        plt.plot(data.index[buy_signals], fastk[buy_signals], '^', markersize=10, color='g', lw=0,
                 label='Сигнал к покупке')
        plt.plot(data.index[sell_signals], fastk[sell_signals], 'v', markersize=10, color='r', lw=0,
                 label='Сигнал к продаже')
        plt.title('Stochastic RSI (StochRSI)')
        plt.legend()
        plt.tight_layout()
        plt.show()

    @staticmethod
    def draw_alma_ribbon(data):
        """
        Creates a visualization of stock price with multiple ALMA indicators.

        Args:
        - data (DataFrame): Input data containing 'Close' prices and multiple 'ALMA' values.

        Returns:
        None
        """
        # Строим график цены и ALMA
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label="Price")
        plt.plot(data["ALMA_VSLOW"], label="ALMA_VSLOW")
        plt.plot(data["ALMA_SLOW"], label="ALMA_SLOW")
        plt.plot(data["ALMA_MIDDLE"], label="ALMA_MIDDLE")
        plt.plot(data["ALMA_FAST"], label="ALMA_FAST")
        plt.plot(data["ALMA_VFAST"], label="ALMA_VFAST")
        plt.title("Stock Price with ALMA")
        plt.xlabel("Date")
        plt.ylabel("USDT")
        plt.legend()
        plt.show()

    @staticmethod
    def draw_avsl(cross_up, cross_down, AVSL, close_prices, data):
        """
        Visualizes AVSL indicators with price data.

        Args:
        - cross_up (array): Array indicating upward crosses.
        - cross_down (array): Array indicating downward crosses.
        - AVSL (array): Array of AVSL values.
        - close_prices (array): Array of close prices.
        - data (DataFrame): Input data for visualization.

        Returns:
        None
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(data.index, close_prices, label='Цена закрытия', color='blue')
        ax.plot(data.index, AVSL, label='AVSL', color='orange')
        ax.scatter(data.index[cross_up], close_prices[cross_up], color='green', label='Пересечение вверх', marker='^',
                   alpha=0.7)
        ax.scatter(data.index[cross_down], close_prices[cross_down], color='red', label='Пересечение вниз', marker='v',
                   alpha=0.7)
        ax.legend()
        ax.set_title('Визуализация AVSL')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()

    @staticmethod
    def draw_bollinger_bands(data):
        """
        Creates a visualization of stock price with Bollinger Bands and trading signals.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', 'Lower Band', 'Buy Signal', and 'Sell Signal'.

        Returns:
        None
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        # Existing code for visualization
        ax.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax.plot(data.index, data['Upper Band'], label='Верхняя полоса', color='red', linestyle='--')
        ax.plot(data.index, data['Middle Band'], label='Средняя полоса', color='black', linestyle='-.')
        ax.plot(data.index, data['Lower Band'], label='Нижняя полоса', color='green', linestyle='--')
        ax.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='grey', alpha=0.1)
        # Signals visualization
        ax.scatter(data.index, data['Buy Signal'], label='Сигнал к покупке', marker='^', color='green')
        ax.scatter(data.index, data['Sell Signal'], label='Сигнал к продаже', marker='v', color='red')
        ax.legend()
        plt.show()

    @staticmethod
    def draw_kama(data):
        """
        Creates a visualization of stock price with KAMA (Kaufman's Adaptive Moving Average) indicator.

        Args:
        - data (DataFrame): Input data containing 'Close' prices and 'KAMA_H' values.

        Returns:
        None
        """
        # Строим график цены и KAMA
        plt.figure(figsize=(12,8))
        plt.plot(data['Close'], label='Price')
        plt.plot(data['KAMA'], label='KAMA')
        plt.title('Btc Price and KAMA')
        plt.xlabel('Date')
        plt.ylabel('USD')
        plt.legend()
        plt.show()

    @staticmethod
    def draw_mama(mama, fama, data, buy_signals, sell_signals):
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

    @staticmethod
    def draw_rsi_clouds(data):
        """Summary:
        Create visualization for RSI Clouds.

        Explanation:
        This static method generates a visualization of the RSI Cloud indicator with buy and sell signals based on the provided data.

        Args:
        - data: The input data containing Close prices.

        Returns:
        None
        """
        overbought = 70
        oversold = 30
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='AAPL Close Price', color='black')
        ax1.scatter(data.index[data['Cross_Up']], data['Close'][data['Cross_Up']], color='green', label='Cross Up',
                    marker='^', alpha=1)
        ax1.scatter(data.index[data['Cross_Down']], data['Close'][data['Cross_Down']], color='red', label='Cross Down',
                    marker='v', alpha=1)
        ax1.set_title('AAPL Stock Price')
        ax1.set_ylabel('Price', color='black')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.legend(loc='upper left')
        ax2.plot(data.index, data['RSI_Short_EMA'], label='RSI Short EMA (7)', color='blue')
        ax2.plot(data.index, data['RSI_Long_EMA'], label='RSI Long EMA (14)', color='orange')
        ax2.scatter(data.index[data['Cross_Up']], data['RSI_Short_EMA'][data['Cross_Up']], color='green',
                    label='Cross Up', marker='^', alpha=1)
        ax2.scatter(data.index[data['Cross_Down']], data['RSI_Short_EMA'][data['Cross_Down']], color='red',
                    label='Cross Down', marker='v', alpha=1)
        ax2.axhline(y=overbought, color='darkred', linestyle='--', label='Overbought (70)')
        ax2.axhline(y=oversold, color='darkgreen', linestyle='--', label='Oversold (30)')
        ax2.set_title('RSI Cloud Indicator with Signals')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('RSI Value', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2.legend(loc='upper right')
        mplcursors.cursor(hover=True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def draw_vwma_based_adx(data):
        """Summary:
        Create visualization of VWMA and ADX trendline.

        Explanation:
        This static method generates a plot showing the Apple stock price with the Weighted Moving Average (WMAV) and ADX trendline highlighted based on the strength of the trend.

        Args:
        - data: The input data containing price, WMAV, and ADX values.

        Returns:
        None
        """
        plt.figure(figsize=(10, 6))
        # Строим график цены
        plt.plot(data.index, data["Close"], label="Price", color='black')
        # Строим график VWMA с изменением цвета в зависимости от силы тренда
        plt.plot(data.index, data["WMAV"], label="WMAV", color='grey')
        plt.plot(data.index[data["ADX_Strong_Trend"]], data["WMAV"][data["ADX_Strong_Trend"]], label="Strong Trend", color='red')
        plt.title("Apple Stock Price with WMAV and ADX Trendline")
        plt.xlabel("Date")
        plt.ylabel("USD")
        # Добавляем сигналы на график
        plt.scatter(data.index[data['Buy_Signal'] == 1], data['Close'][data['Buy_Signal'] == 1], label='Buy',
                    marker='^', color='green')
        plt.scatter(data.index[data['Sell_Signal'] == -1], data['Close'][data['Sell_Signal'] == -1], label='Sell',
                    marker='v', color='red')

        plt.legend()
        plt.show()

    @staticmethod
    def draw_zigzag(data_peaks_valleys):
        """Summary:
        Plot the ZigZag indicator.

        Explanation:
        This static method generates a plot of the ZigZag indicator based on the peaks and valleys data provided.

        Args:
        - data_peaks_valleys: DataFrame containing date and ZigZag values for peaks and valleys.

        Returns:
        None
        """
        plt.figure(figsize=(10, 10))
        plt.plot(data_peaks_valleys["date"], data_peaks_valleys["zigzag_y"], color="blue", label="ZigZag")

        # Добавляем горизонтальные отрезки для каждой точки ZigZag
        for i in range(len(data_peaks_valleys) - 1):
            plt.hlines(y=data_peaks_valleys.iloc[i]["zigzag_y"], xmin=data_peaks_valleys.iloc[i]["date"], xmax=data_peaks_valleys.iloc[i + 1]["date"], color="green", linestyle=":", linewidth=1)

        plt.legend()
        plt.title('ZigZag Indicator')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()