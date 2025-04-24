import contextlib, asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union

def prepare_data_to_dataframe(result:dict) -> list:
    lenghts = len(result["data"])
    data_list = []
    for i in range(lenghts):
        data_dict = {
            'Date': datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3),
            'Open': float(result["data"][i][1]),
            'High': float(result["data"][i][2]),
            'Low': float(result["data"][i][3]),
            'Close': float(result["data"][i][4]),
            'Volume': float(result["data"][i][6]),
            'Volume Usdt': float(result["data"][i][7])
        }
        data_list.append(data_dict)
    return data_list


def prepare_many_data_to_append_db(result: dict) -> dict:
    time, _open, high, low, _close, volume, volume_usdt = [], [], [], [], [], [], []
    for i in range(len(result['data'])):
        time.append(datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3))
        _open.append(result["data"][i][1])
        high.append(result["data"][i][2])
        low.append(result["data"][i][3])
        _close.append(result['data'][i][4])
        volume.append(result['data'][i][6])
        volume_usdt.append(result['data'][i][5])
    return {
        "Date": time,
        "Open": _open,
        "High": high,
        "Low": low,
        "Close": _close,
        "Volume": volume,
        "Volume Usdt": volume_usdt
    }


def create_dataframe(data_list: dict) -> pd.DataFrame:
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Volume Usdt']
    if missing_columns := set(required_columns) - set(data_list.keys()):
        raise ValueError(f"Missing required columns in data_list: {', '.join(missing_columns)}")
    data_rows = [
        {
            'Date': pd.to_datetime(datetime_value),
            'Open': open_value,
            'High': high_value,
            'Low': low_value,
            'Close': close_value,
            'Volume': volume_value,
            'Volume Usdt': volume_usdt_value
        }
        for datetime_value, open_value, high_value, low_value, close_value, volume_value, volume_usdt_value in zip(
            data_list['Date'], data_list['Open'], data_list['High'], data_list['Low'], data_list['Close'],
            data_list['Volume'], data_list['Volume Usdt']
        )
    ]
    data_frame = pd.DataFrame(data_rows)
    data_frame['Open'] = data_frame['Open'].astype(np.float64)
    data_frame['High'] = data_frame['High'].astype(np.float64)
    data_frame['Low'] = data_frame['Low'].astype(np.float64)
    data_frame['Close'] = data_frame['Close'].astype(np.float64)
    data_frame['Volume'] = data_frame['Volume'].astype(np.float64)
    data_frame['Volume Usdt'] = data_frame['Volume Usdt'].astype(np.float64)
    data_frame.set_index('Date', inplace=True)
    return data_frame.sort_values(by='Date', ascending=True)


def create_timestamp(time:Union[str, None]=None) -> int:
    if time is None:
        return time
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H', '%Y-%m-%d']
    formated_time = None
    for fmt in formats:
        try:
            date_time_obj = datetime.strptime(time, fmt)
            if fmt == '%Y-%m-%d':
                date_time_obj = date_time_obj.replace(hour=0, minute=0, second=0)
            elif fmt == '%Y-%m-%d %H':
                date_time_obj = date_time_obj.replace(minute=0,second=0)
            formated_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
            break
        except ValueError:
            continue
    if not formated_time:
        raise ValueError(f"Unable to recognize date and time format: {time}")
    date_time_obj = datetime.strptime(formated_time, '%Y-%m-%d %H:%M:%S')
    timestamp = int(date_time_obj.timestamp())
    return timestamp


# Можешь добавить рассчёт возможного кол-ва  баров по таймфрему чтобы ошибки не было при вызове after c limit=300
def validate_get_data_params(
    history:bool, lengths:Optional[int] = None, load_data_before:Optional[str]=None, load_data_after:Optional[str]=None,
    timeframe:Optional[str]=None) -> dict:
    with contextlib.suppress(Exception):
        load_data_after = create_timestamp(load_data_after)
    with contextlib.suppress(Exception):
        load_data_before = create_timestamp(load_data_before)
    if not history and isinstance(lengths, int) and lengths > 300:
        raise ValueError('Lenght 300 for method get candlestick history is max')
    if history and isinstance(lengths, int) and lengths > 100:
        raise ValueError('Lenght 100 for method get candlestick history is max')
    if isinstance(lengths, (str, type(None))):
        lengths = ''
    limit = lengths or ' '
    before = load_data_before or ' '
    after = load_data_after or ' '
    return {'limit': limit, 'before': before, 'after': after}




def generate_time_points(num_groups: int, timeframe:Optional[str] = None) -> list:
    #Работает только с H4, можешь модифицировать под нужные тф(5m, 15m, 1H, 1D)
    current_time = datetime.now()
    rounded_time = current_time.replace(minute=0, second=0, microsecond=0)
    while rounded_time.hour % 4 != 0:
        rounded_time -= timedelta(hours=1)
    time_points = []
    for _ in range(num_groups):
        time_list = [rounded_time - timedelta(hours=4 * i) for i in range(300)]
        time_points.extend(
            (
                time_list[0].strftime('%Y-%m-%d %H:%M:%S'),
                time_list[-2].strftime('%Y-%m-%d %H:%M:%S'),
            )
        )
        rounded_time = time_list[-2]
    return list(time_points)


