import json, time, logging
from datetime import datetime
from decimal import Decimal
import okx.PublicData as PublicData
import okx.Account as Account
import okx.Trade as Trade


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
 у которого есть разрешения на вывод и торговлю(отдельно),
   то он автоматически удалиться через 14 дней.
"""

class UserInfo:
    def __init__(self, api_key, secret_key, passphrase, flag):
        self.tradeApi = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        

    # Проверка баланса
    def check_balance(self):
        result_bal = self.accountAPI.get_account_balance()
        usdt_balance = Decimal(result_bal["data"][0]["details"][0]["availBal"])  # получаем значение ключа ccy по указанному пути
        balance = float(usdt_balance)
        print(f'Баланс: \n {result_bal}\n\n')
        return balance


    # Установка левериджа кросс позиций для отдельного инструмента
    def set_leverage_inst(self, instId, leverage, mgnMode):
        result = self.accountAPI.set_leverage(
            instId=instId,
            lever=leverage,
            mgnMode=mgnMode #cross или isolated
        )
        print(f'Установка левириджа {leverage}x, кросс для {instId}: \n{result}\n\n')


    # Установка левериджа для \изолированых позиций для шорт и лонг
    def set_leverage_short_long(self, instId, leverage, posSide, mgnMode):
        result = self.accountAPI.set_leverage(
            instId = instId,
            lever = leverage,
            posSide = posSide,
            mgnMode = mgnMode
        )
        print(f'Установка левериджа {leverage}x, для изолированных лонг {instId}: \n{result}\n\n')


    # Установка режима торговли
    def set_trading_mode(self):
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        print(result)