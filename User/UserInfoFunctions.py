from decimal import Decimal
import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as MarketData
from User.LoadSettings import LoadUserSettingData
from datasets.RedisCache import RedisCache
from docx import Document


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class UserInfo(LoadUserSettingData, RedisCache):
    def __init__(self):
        super().__init__(key='contracts_prices')
        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)

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
        
    def check_instrument_info(self, instId:str):
        result = self.marketDataAPI.get_ticker(instId=instId)
        print(result)


    def check_contract_price(self, save=None|bool):
        result = self.accountAPI.get_instruments(instType="SWAP")
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)

    
    
    def check_contract_price_cache(self, instId:str):
        result = super().load_message_from_cache()
        return float(next(
                (
                    instrument['ctVal']
                    for instrument in result['data']
                    if instrument['instId'] == instId
                ),
                None,
            ))
        




    
    
