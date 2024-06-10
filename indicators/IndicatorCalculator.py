import numpy as np
import talib


class IndicatorCalculator:

    @staticmethod
    def avsl(data):
        def _avsl_price_fun(VPC, VPR, VM, src):
            """
            Calculates the price step based on volume, price, and source data.

            Args:
            - VPC (array): Array of VPC values.
            - VPR (array): Array of VPR values.
            - VM (array): Array of VM values.
            - src (array): Source data array.

            Returns:
            - PriceV (array): Array of calculated price steps.
            """
            priceV = np.zeros_like(VPC)  # Создаем массив нулей той же формы, что и VPC
            for i in range(len(VPC)):
                VPCI = VPC[i] * VPR[i] * VM[i]
                if np.isnan(VPCI):  # Проверяем, является ли VPCI NaN
                    lenV = 0
                else:
                    lenV = int(round(abs(VPCI - 3))) if VPC[i] < 0 else round(VPCI + 3)
                VPCc = -1 if (-1 < VPC[i] < 0) else 1 if (1 > VPC[i] >= 0) else VPC[i]
                price = np.sum(src[i - lenV + 1:i + 1] / VPCc / VPR[i - lenV + 1:i + 1]) if lenV > 0 else src[i]
                priceV[i] = price / lenV / 100 if lenV > 0 else price
            return priceV

        def _prepare_calculate_avsl(data):
            """
            Prepares data and parameters for calculating AVSL indicators.

            Args:
            - data (DataFrame): Input data containing 'Adj Close', 'Low', and 'Volume' columns.

            Returns:
            - Tuple: A tuple containing processed data and parameters for AVSL calculation.
            """
            # Подготовка данных
            close_prices = data['Close'].values.astype('float64')
            low_prices = data['Low'].values.astype('float64')
            volumes = data['Volume'].values.astype('float64')
            # Параметры
            lenghtsFast = 34  # Быстрая скользящая средняя
            lenghtsSlow = 134  # Медленная скользящая средняя
            lenT = 9  # Сигнал для VPCI
            standDiv = 3.0  # Стандартное отклонение
            offset = 2  # Смещение
            # Расчеты
            VWmaS = talib.WMA(close_prices, timeperiod=lenghtsSlow)  # Медленная VWMA
            VWmaF = talib.WMA(close_prices, timeperiod=lenghtsFast)  # Быстрая VWMA
            AvgS = talib.SMA(close_prices, timeperiod=lenghtsSlow)  # Медленная средняя объема
            AvgF = talib.SMA(close_prices, timeperiod=lenghtsFast)  # Быстрая средняя объема
            VPC = VWmaS - AvgS  # VPC+/-
            VPR = VWmaF / AvgF  # Отношение цены к объему
            VM = talib.SMA(volumes, timeperiod=lenghtsFast) / talib.SMA(volumes,
                                                                        timeperiod=lenghtsSlow)  # Множитель объема
            VPCI = VPC * VPR * VM  # Индикатор VPCI
            DeV = standDiv * VPCI * VM  # Отклонение
            return close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow

        """
        Calculates AVSL indicators based on the provided data.

        Args:
        - data (DataFrame): Input data containing 'Adj Close', 'Low', and 'Volume' columns.

        Returns:
        - Tuple: A tuple containing cross up, cross down signals, AVSL values, close prices and signal at last bar.
        """
        close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow = _prepare_calculate_avsl(data)
        PriceV = _avsl_price_fun(VPC, VPR, VM, low_prices)
        AVSL = talib.SMA(low_prices - PriceV + DeV, timeperiod=lenghtsSlow)
        cross_up = (close_prices > AVSL) & (np.roll(close_prices, 1) <= np.roll(AVSL, 1))
        cross_down = (close_prices < AVSL) & (np.roll(close_prices, 1) >= np.roll(AVSL, 1))
        # Проверка наличия сигнала на последнем баре
        last_bar_signal = None
        if cross_up[-1]:
            last_bar_signal = 'cross_up'
        elif cross_down[-1]:
            last_bar_signal = 'cross_down'
        return cross_up, cross_down, AVSL, close_prices, last_bar_signal

    @staticmethod
    def bollinger_bands(data, lenghts, stdev):
        """
                Calculates Bollinger Bands based on the given data, lengths, and standard deviations.

                Args:
                - data (DataFrame): Input data containing 'High' and 'Low' prices.
                - lenghts (int): Length of the moving average window.
                - stdev (int): Standard deviation multiplier for the bands.

                Returns:
                - DataFrame: Data with added columns for Upper Band, Middle Band, and Lower Band.
                """
        high_low_average = (data['High'] + data['Low']) / 2
        upper_band, middle_band, lower_band = talib.BBANDS(
            high_low_average,
            timeperiod=lenghts,
            nbdevup=stdev,
            nbdevdn=stdev,
            matype=0
        )
        data['Upper Band'] = upper_band
        data['Middle Band'] = middle_band
        data['Lower Band'] = lower_band
        return data

    @staticmethod
    def kama(data, period, fast, slow):
        """
               Calculates the Kaufman's Adaptive Moving Average (KAMA) values based on the given data, period, fast, and slow parameters.

               Args:
               - data (DataFrame): Input data containing 'High' and 'Low' prices.
               - period (int): Period for calculating KAMA. 54 Defolt
               - fast (int): Fast smoothing constant. 3 Defolt
               - slow (int): Slow smoothing constant. 34 Defolt

               Returns:
               - array: Array of KAMA values.
               """
        # Вычисляем направление и волатильность
        direction = abs(((data['High'] - data['High'].shift(period)) + (data['Low'] - data['Low'].shift(period))) / 2)
        volatility = (data['High'].diff().abs().rolling(period).sum() + data['Low'].diff().abs().rolling(
            period).sum()) / 2 + 0.0001  # добавим небольшое число к волатильности
        # Вычисляем коэффициент эффективности
        er = direction / volatility
        # Вычисляем сглаживающую константу
        sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
        # Вычисляем KAMA
        kama = np.zeros(len(data))
        kama[period] = (data['High'].iloc[period] + data['Low'].iloc[period]) / 2  # используем среднее между high и low
        for i in range(period + 1, len(data)):
            # используем .iloc[] для sc
            kama[i] = kama[i - 1] + sc.iloc[i] * ((data['High'].iloc[i] + data['Low'].iloc[i]) / 2 - kama[i - 1])
        data['KAMA'] = kama
        return data

    @staticmethod
    def mama(data):
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
        return mama, fama, data, buy_signals, sell_signals
