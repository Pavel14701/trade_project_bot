import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def prepare_data_to_dataframe(result) -> list:
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


def prepare_many_data_to_append_db(result) -> dict:
    time = []
    _open = []
    high = []
    low = []
    _close = []
    volume = []
    volume_usdt  = []
    for i in range(len(result['data'])):
        time.append(datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3))
        _open.append(result["data"][i][1])
        high.append(result["data"][i][2])
        low.append(result["data"][i][3])
        _close.append(result['data'][i][4])
        volume.append(result['data'][i][6])
        volume_usdt.append(result['data'][i][5])
    return {
        "Datr": time,
        "Open": _open,
        "High": high,
        "Low": low,
        "Close": _close,
        "Volume": volume,
        "Volume Usdt": volume_usdt
    }


def create_dataframe(data_list: dict) -> pd.DataFrame:
    required_columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'volume_usdt']
    if missing_columns := set(required_columns) - set(data_list.keys()):
        raise ValueError(f"Missing required columns in data_list: {', '.join(missing_columns)}")
    data_rows = [
        {
            'Datetime': pd.to_datetime(datetime_value),
            'Open': open_value,
            'High': high_value,
            'Low': low_value,
            'Close': close_value,
            'Volume': volume_value,
            'Usdt Volume': volume_usdt_value
        }
        for datetime_value, open_value, high_value, low_value, close_value, volume_value, volume_usdt_value in zip(
            data_list['Date'], data_list['Open'], data_list['High'], data_list['Low'], data_list['Close'],
            data_list['Volume'], data_list['Volume Usdt']
        )
    ]
    data_frame = pd.DataFrame(data_rows)
    data_frame['Date'] = data_frame['Date']
    data_frame['Open'] = data_frame['Open'].astype(np.float64)
    data_frame['High'] = data_frame['High'].astype(np.float64)
    data_frame['Low'] = data_frame['Low'].astype(np.float64)
    data_frame['Close'] = data_frame['Close'].astype(np.float64)
    data_frame['Volume Usdt'] = data_frame['Volume Usdt'].astype(np.float64)
    data_frame.set_index('Date', inplace=True)
    return data_frame



def create_message_state_avsl_rsi_clouds(
    instId:str, timeframe:str, avsl:float,
    adx=None|float, rsi=None|str) -> dict:
    return dict([
        ('time', datetime.now().isoformat()),
        ('instId', instId),
        ('timeframe', timeframe),
        ('strategy', 'avs_rsi_clouds'),
        ('trend_strenghts', adx),
        ('signal', rsi),
        ('slPrice', avsl['last'])
    ])


def create_timestamp(time:str) -> int:
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
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
        raise ValueError(f"Не удалось распознать формат даты и времени: {time}")
    date_time_obj = datetime.strptime(formated_time, '%Y-%m-%d %H:%M:%S')
    timestamp = int(date_time_obj.timestamp())
    return timestamp