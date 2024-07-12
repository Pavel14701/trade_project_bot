import pandas as pd
from User.UserInfoFunctions import UserInfo
from datasets.database import DataAllDatasets


bd = DataAllDatasets('BTC-USDT-SWAP', '4H')
get = UserInfo('BTC-USDT-SWAP', '4H')
timestamps = []
for timestamp in timestamps:
    result = get.get_market_data(load_data_after=timestamp)
    bd.add_data_to_db(result)
data = bd.get_all_bd_marketdata()
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)
print(df)
