import yfinance as yf, pandas as pd, numpy as np
from indicators.adx_ind import ADXTrend
from indicators.avsl_ind import AVSLIndicator
from indicators.rsi_clouds_ind import CloudsRsi
from datasets.database import DataAllDatasets
from datasets.tables import create_tables
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from typing import Dict, Optional


# Набросок, нужно смотреть формат yfinance, подгонять под формат рассчётов индикаторов,
# продумать все критерии для анализа(не только сколько выдаёт на дистанции но и устойчивость стратегии
# по разным параметрам: коэф Пирсона, коэф Фишера, анализ кореляций и т.д.)
# Пока задача стоит просто вывести сигналы на покупку и на продажу в датафрейм вот так:
'''
InstId    Date              Signal  Size  Balance   Event  Price  Profit(Loss)  SL      TP
BTC-USDT  22-04-2024 18:34  long    286$  7345.67$  Open   54830  None          54730$  None
BTC-USDT  01-05-2024 18:34  short   286$  7345.67$  Close  55800  +100$(calc%   None    None
                                                                  to deposit)
BTC-USDT  01-05-2024 18:34  short   286$  7345.67$  Open   55800  None          56300    None
'''


class Simulation:
    def __init__(self, instId:str, after:str, before:str, timeframe:str, strategy:str, use_db:Optional[bool]=None) -> None:
        self.instId, self.after, self.before, self.timeframe = instId, after, before, timeframe
        self.strategy = strategy
        self.use_db = use_db


    def __create_db_instance(self) -> None:
        self.Session, self.classes_dict = create_tables(True, self.instId, self.timeframe)
        self.db = DataAllDatasets(self.Session, self.classes_dict, self.instId, self.timeframe, True)


    def __prepare_data_to_save(self, data: pd.DataFrame) -> pd.DataFrame:
        data.rename(columns={'Adj Close': 'Volume Usdt'}, inplace=True)
        data.rename_axis('Date', inplace=True)
        return data


    def __load_test_data(self) -> None:
        data = yf.download(self.instId, self.after, self.before, interval=self.timeframe)
        print(type(data))
        self.data = self.__prepare_data_to_save(data)
        print(self.data)
        self.db.save_charts(self.data)


    def __calc_avsl_rsi_clouds(self) -> Dict[str, pd.DataFrame]:
        with ThreadPoolExecutor() as executor:
            #ПРОБЛЕМЫ ТУТ
            adx_future = executor.submit(ADXTrend(self.data, False)._calculate_adx_sync)
            rsi_clouds_future = executor.submit(CloudsRsi(self.data,False).calculate_rsi_macd)
            avsl_future = executor.submit(AVSLIndicator(self.data, False).calculate_avsl)
            return adx_future.result(), rsi_clouds_future.result(), avsl_future.result()


    def __validate_strategy(self) -> pd.DataFrame:
        match self.strategy:
            case 'avsl_rsi_clouds':
                adx, rsi_clouds, avsl = self.__calc_avsl_rsi_clouds()
                print(f'\n{adx}\n')
                print(f'\n{avsl}\n')
                print(f'\n{rsi_clouds}\n')
                return self.__merge_data(adx, rsi_clouds, avsl)


    def __merge_data(self, *args) -> pd.DataFrame:
        dfs = list(args)
        return reduce(lambda left, right: pd.merge(left, right, on='Date'), dfs)


    def __prepare_data_for_rsi_clouds(self, data:pd.DataFrame):
        return data


    def __create_series_loss_profit(self, data:pd.DataFrame) -> pd.DataFrame:
        match self.strategy:
            case 'avsl_rsi_clouds':
                return self.__prepare_data_for_rsi_clouds(data)


    def create_simulation(self) -> pd.DataFrame:
        self.__create_db_instance()
        self.__load_test_data()
        data = self.__validate_strategy()
        return data



class StrategyTester:
    def __init__(self, data:pd.DataFrame, strategy:str, **kwargs):
        self.data = data
        self.strategy = kwargs['strategy']


    def check_results(self):
        pass


data = Simulation('BTC-USD', '2024-01-01', '2024-08-01', '1h', 'avsl_rsi_clouds').create_simulation()
print(data)

"""
# Загрузка данных
ticker = yf.download('BTC-USD', '2024-01-01', '2024-08-01', interval='1h')
# Проверка столбцов
print(ticker.columns)
# Сброс индекса, чтобы 'Datetime' стал столбцом
ticker.reset_index(inplace=False)
print(ticker)
# Удаление информации о временной зоне
#ticker['Datetime'] = ticker['Datetime'].dt.tz_localize(None)
# Сохранение в Excel
ticker.to_excel('abcde.xlsx', index=False)
"""
