from okx import MarketData
from User.LoadSettings import LoadUserSettingData

settings = LoadUserSettingData()
user_settings = settings.load_user_settings()


marketDataAPI = MarketData.MarketAPI(user_settings[0])
result = marketDataAPI.get_candlesticks(
    instId='ETH-USDT-SWAP',
    after='',
    before='',
    bar='15m',
    limit=300 # 300 Лимит Okx на 1 реквест
)
print(len(result['data']))