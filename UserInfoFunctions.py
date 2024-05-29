#from decimal import Decimal



class UserInfo:
    def __init__(self, api_key, secret_key, passphrase, flag):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.flag = flag  # live trading: 0, demo trading: 1
        
    # Проверка баланса
    def check_balance(self):
        accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        result_bal = accountAPI.get_account_balance()
        usdt_balance = Decimal(result_bal["data"][0]["details"][0]["availBal"])  # получаем значение ключа ccy по указанному пути
        usdt_balance = int(usdt_balance)
        print(usdt_balance)  # выводим значение на экран
        print(f'Баланс: \n {result_bal}\n\n')
        return usdt_balance

    # Пример использования класса:
    # user_info = UserInfo('ваш_api_key', 'ваш_secret_key', 'ваш_passphrase', '1')
    # user_info.check_balance()

    # Установка левериджа кросс позиций для отдельного инструмента
    def set_leverage_inst(self, instId, lever, mgnMode):
        result = self.accountAPI.set_leverage(
            instId=instId,
            lever=lever,
            mgnMode=mgnMode #cross или isolated
        )
        print(f'Установка левириджа {lever}x, кросс для {instId}: \n{result}\n\n')

    # Установка левериджа для \изолированых позиций для шорт и лонг
    def set_leverage_short_long(self, instId, lever, posSide, mgnMode)
        instId = "BTC-USDT-SWAP"
        result = accountAPI.set_leverage(
            instId = instId,
            lever = lever,
            posSide = posSide,
            mgnMode = mgnMode
        )
        print(f'Установка левериджа для изолированных лонг {instId}: \n{result}\n\n')
    
    # Установка режима торговли
    def set_trading_mode():
      result = accountAPI.set_position_mode(
          posMode="long_short_mode"
      )
      print(result)

