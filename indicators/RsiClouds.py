import talib



from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer


class CloudsRsi:
    """Summary:
    Class for calculating and visualizing RSI Clouds.

    Explanation:
    This class provides static methods to calculate RSI values for short and long periods, smooth them using EMA, detect crossover signals, and create a visualization of the RSI Cloud indicator with buy and sell signals.

    Args:
    - data: The input data containing Close prices.
    - rsi_period_short: The short period for RSI calculation.
    - rsi_period_long: The long period for RSI calculation.
    - ema_period: The period for EMA smoothing.

    Returns:
    - For calculate_rsi_clouds: DataFrame with RSI Short EMA, RSI Long EMA, Cross Up, and Cross Down signals.
    - For create_vizualization_rsi_clouds: None
    """

    @staticmethod
    def calculate_rsi_clouds(data, rsi_period_short, rsi_period_long, ema_period):
        """Summary:
        Calculate RSI values and crossover signals for RSI Clouds.

        Explanation:
        This static method calculates RSI values for short and long periods, smoothes them using EMA, and detects crossover signals to determine buy and sell points.

        Args:
        - data: The input data containing Close prices.
        - rsi_period_short: The short period for RSI calculation.
        - rsi_period_long: The long period for RSI calculation.
        - ema_period: The period for EMA smoothing.

        Returns:
        - DataFrame with RSI Short EMA, RSI Long EMA, Cross Up, and Cross Down signals.
        """
        # Вычисляем RSI для двух периодов
        rsi_short = talib.RSI(data['Close'].values, timeperiod=rsi_period_short)
        rsi_long = talib.RSI(data['Close'].values, timeperiod=rsi_period_long)
        # Сглаживаем RSI с помощью EMA
        rsi_short_ema = talib.EMA(rsi_short, timeperiod=ema_period)
        rsi_long_ema = talib.EMA(rsi_long, timeperiod=ema_period)
        # Добавляем индикаторы в DataFrame
        data['RSI_Short_EMA'] = rsi_short_ema
        data['RSI_Long_EMA'] = rsi_long_ema
        # Сигналы пересечения
        cross_up = (data['RSI_Short_EMA'] > data['RSI_Long_EMA']) & (
                    data['RSI_Short_EMA'].shift(1) <= data['RSI_Long_EMA'].shift(1))
        cross_down = (data['RSI_Short_EMA'] < data['RSI_Long_EMA']) & (
                    data['RSI_Short_EMA'].shift(1) >= data['RSI_Long_EMA'].shift(1))
        # Добавляем сигналы в DataFrame
        data['Cross_Up'] = cross_up
        data['Cross_Down'] = cross_down
        return data


#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = CloudsRsi.calculate_rsi_clouds(data, rsi_period_short = 7, rsi_period_long = 14, ema_period = 9)
IndicatorDrawer.draw_rsi_clouds(data)


