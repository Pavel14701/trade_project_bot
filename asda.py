import pandas as pd
from User.UserInfoFunctions import UserInfo
from datasets.database import DataAllDatasets


bd = DataAllDatasets('BTC-USDT-SWAP', '4H')
data = bd.get_all_bd_marketdata()
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)
print(df)
