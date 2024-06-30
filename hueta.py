import json
from User.UserInfoFunctions import UserInfo

a = UserInfo()
data = a.check_instruments_info('BTC-USDT-SWAP', False)
ctVal = next(
    (
        instrument['ctVal']
        for instrument in data['data']
        if instrument['instId'] == 'BTC-USD-SWAP'
    ),
    None,
)
print(ctVal)
