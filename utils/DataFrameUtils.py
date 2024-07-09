import pandas as pd
from datetime import datetime, timedelta

def prepare_data_to_dataframe(result) -> list:
    lenghts = len(result["data"])
    data_list = []
    for i in range(lenghts):
        data_dict = {
            'time': datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3),
            'open': float(result["data"][i][1]),
            'high': float(result["data"][i][2]),
            'low': float(result["data"][i][3]),
            'close': float(result["data"][i][4]),
            'volume': float(result["data"][i][6]),
            'volume_usdt': float(result["data"][i][7])
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
        volume.append(result['data'][i][5])
        volume_usdt.append(result['data'][i][6])
    return {
        "time": time,
        "open": _open,
        "high": high,
        "low": low,
        "close": _close,
        "volume": volume,
        "volume_usdt": volume_usdt
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
            data_list['time'], data_list['open'], data_list['high'], data_list['low'], data_list['close'],
            data_list['volume'], data_list['volume_usdt']
        )
    ]
    data_frame = pd.DataFrame(data_rows)
    if 'time' in data_list:
        data_frame['Datetime'] = pd.to_datetime(data_list['time'])
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