import pandas as pd
from User.UserInfoFunctions import UserInfo
from datasets.database import DataAllDatasets
from utils.DataFrameUtils import generate_time_points, prepare_many_data_to_append_db


bd = DataAllDatasets('ETH-USDT-SWAP', '4H')
get = UserInfo('ETH-USDT-SWAP', '4H')
dates = generate_time_points(20)
for date in dates:
    print(date)
    result = get.get_market_data(300, None, date)
    result = prepare_many_data_to_append_db(result)
    bd.save_charts(result)
data = bd.get_all_bd_marketdata()
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)
print(df)
