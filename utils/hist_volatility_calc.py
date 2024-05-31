import statistics as stat
import math
import decimal


class CalculateHistoricVolatility:
    def __init__(self, data, timeframes, instId):
        self.data = data
        self.timeframes = timeframes
        self.instId = instId


    # Рассчёт коэффициента волатильности(два варианта хз какой использовать) вариант 1
    def calc_volat_coef_v1(self):
        # Можно вытянуть часть этой функции в класс DataBase
        # Разбиваем словарь на несколько словарей по временным интервалам
        data_15m = data['15m']
        data_1H = data['1H']
        data_4H = data['4H']
        data_1D = data['1D']
        columns = ["low", "open"]
        # Преобразуем datetime.datetime и decimal в значения
        for d in [data_15m, data_1H, data_4H, data_1D]:
            for key, value in d.items():
                if key == 'date':
                    # Преобразуем datetime.datetime в строки
                    d[key] = [x.strftime('%Y-%m-%d %H:%M:%S') for x in value]
                else:
                    d[key] = [decimal.Decimal(x) for x in value]
        low_15m = data_15m['low']
        high_15m = data_15m['high']
        low_1H = data_1H['low']
        high_1H = data_1H['high']
        low_4H = data_4H['low']
        high_4H = data_4H['high']
        low_1D = data_1D['low']
        high_1D = data_1D['high']
        data = {
            'low_15m': low_15m,
            'high_15m': high_15m,
            'ext_15m': low_15m + high_15m,
            'low_1H': low_1H,
            'high_1H': high_1H,
            'ext_1H': low_1H + high_1H,
            'low_4H': low_4H,
            'high_4H': high_4H,
            'ext_4H': low_4H + high_4H,
            'low_1D': low_1D,
            'high_1D': high_1D,
            'ext_1D': low_1D + high_1D
        }
        # рассчёт кэфа волатильности(варик 1)
        #15 минут
        st_dev_15m = stat.stdev(data['ext_15m'])
        mean_15m = stat.mean(data['ext_15m'])
        vol_coef_15m = st_dev_15m / mean_15m * 100
        print(st_dev_15m, mean_15m, vol_coef_15m)
        #1 час
        st_dev_1H = stat.stdev(data['ext_1H'])
        mean_1H = stat.mean(data['ext_1H'])
        vol_coef_1H = st_dev_1H / mean_1H * 100
        print(st_dev_1H, mean_1H, vol_coef_1H)
        # 4 часа
        st_dev_4H = stat.stdev(data['ext_4H'])
        mean_4H = stat.mean(data['ext_4H'])
        vol_coef_4H = st_dev_4H / mean_4H * 100
        print(st_dev_4H, mean_4H, vol_coef_4H)
        # 1 день
        st_dev_1D = stat.stdev(data['ext_1D'])
        mean_1D= stat.mean(data['ext_1D'])
        vol_coef_1D = st_dev_1D / mean_1D * 100
        print(st_dev_1D, mean_1D, vol_coef_1D)
        return (vol_coef_15m, vol_coef_1H, vol_coef_4H, vol_coef_1D)


    # Рассчёт коэффициента волатильности(два варианта хз какой использовать) вариант 2
    def calc_volat_coef_v2(self):
        # Можно вытянуть часть этой функции в класс DataBase
        # Разбиваем словарь на несколько словарей по временным интервалам
        data_15m = data['15m']
        data_1H = data['1H']
        data_4H = data['4H']
        data_1D = data['1D']
        columns = ["low", "open"]
        # Преобразуем datetime.datetime и decimal в значения
        for d in [data_15m, data_1H, data_4H, data_1D]:
            for key, value in d.items():
                if key == 'date':
                    # Преобразуем datetime.datetime в строки
                    d[key] = [x.strftime('%Y-%m-%d %H:%M:%S') for x in value]
                else:
                    d[key] = [decimal.Decimal(x) for x in value]
        low_15m = data_15m['low']
        high_15m = data_15m['high']
        low_1H = data_1H['low']
        high_1H = data_1H['high']
        low_4H = data_4H['low']
        high_4H = data_4H['high']
        low_1D = data_1D['low']
        high_1D = data_1D['high']
        data = {
            'low_15m': low_15m,
            'high_15m': high_15m,
            'ext_15m': low_15m + high_15m,
            'low_1H': low_1H,
            'high_1H': high_1H,
            'ext_1H': low_1H + high_1H,
            'low_4H': low_4H,
            'high_4H': high_4H,
            'ext_4H': low_4H + high_4H,
            'low_1D': low_1D,
            'high_1D': high_1D,
            'ext_1D': low_1D + high_1D
        }
        vol_dict = {}
        for timeframe in self.timeframes:
            log_returns = []
            for i in range(len(self.data[f"high_{timeframe}"]) - 1, 0, -1):
                current_price = (self.data[f"high_{timeframe}"][i] + self.data[f"low_{timeframe}"][i]) / 2
                previous_price = (self.data[f"high_{timeframe}"][i - 1] + self.data[f"low_{timeframe}"][i - 1]) / 2
                log_return = math.log(current_price) - math.log(previous_price)
                log_returns.append(log_return)
            # Вычисляем стандартное отклонение логарифмических доходностей
            std_dev = math.sqrt(sum([(x - sum(log_returns) / len(log_returns)) ** 2 for x in log_returns]) / (len(log_returns) - 1))
            # Вычисляем волатильность
            vol = std_dev * math.sqrt(365)
            vol_dict[timeframe] = vol
        vol_coef_15m = vol_dict.get("15m", None)
        vol_coef_1H = vol_dict.get("1H", None)
        vol_coef_4H = vol_dict.get("4H", None)
        vol_coef_1D = vol_dict.get("1D", None)
        # Возвращаем кортеж значений волатильности
        return (vol_coef_15m, vol_coef_1H, vol_coef_4H, vol_coef_1D)