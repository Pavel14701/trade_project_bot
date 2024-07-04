from utils.IventListner import OKXIventListner
from User.UserInfoFunctions import UserInfo

info = UserInfo()
info.check_contract_price(False)
pos_listner = OKXIventListner('ETH-USDT-SWAP')

if __name__ == '__main__':
    pos_listner.create_listner()
