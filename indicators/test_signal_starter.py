from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer
from IndicatorCalculator import IndicatorCalculator
from IndicatorSignals import IndicatorSignals

data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = IndicatorCalculator.bollinger_bands(data, lenghts=34, stdev=2)
print(data)
data = IndicatorSignals.bollinger_bands_signal(data)
IndicatorDrawer.draw_bollinger_bands(data)

data = IndicatorSignals.kama_signal(IndicatorCalculator.kama(data, period=54, fast=3, slow=34))
IndicatorDrawer.draw_kama(data)
