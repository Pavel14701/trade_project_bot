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


def prepare_many_data_to_append_db(result, i, instId, timeframe) -> dict:
    return {
        "instId": instId,
        "timeframe": timeframe,
        "time": datetime.fromtimestamp(int(result["data"][i][0])/1000) + timedelta(hours=3),
        "open": result["data"][i][1],
        "close": result["data"][i][2],
        "high": result["data"][i][3],
        "low": result["data"][i][4],
        "volume": result["data"][i][6],
        "volume_usdt": result["data"][i][7]
    }
    
def create_dataframe(data_list) -> pd.Dataframe:
    data_frame = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Usdt Volume'])
    data_frame = pd.DataFrame(data_list)
    data_frame['Datetime'] = pd.to_datetime(data_frame['Datetime'])
    data_frame['Open'] = data_frame['Open'].astype(float)
    data_frame['High'] = data_frame['High'].astype(float)
    data_frame['Low'] = data_frame['Low'].astype(float)
    data_frame['Close'] = data_frame['Close'].astype(float)
    data_frame['Volume'] = data_frame['Volume'].astype(float)
    data_frame['Usdt Volume'] = data_frame['Usdt Volume'].astype(float)
    return data_frame


def create_message_state(instId:str, timeframe:str, avsl:float, adx=None|float, rsi=None|str) -> dict:
    current_time = datetime.now()
    formatted_time = current_time.isoformat()
    return dict([
        ("time", formatted_time),
        ("instId", instId),
        ("timeframe", timeframe),
        ("trend_strenghts", adx),
        ("signal", rsi),
        ("slPrice", avsl['last'])
    ])