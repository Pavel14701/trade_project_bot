from decimal import Decimal
import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as MarketData
from User.LoadSettings import LoadUserSettingData
from datasets.RedisCache import RedisCache
from utils.LoggingFormater import MultilineJSONFormatter
from docx import Document


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class UserInfo(RedisCache, LoadUserSettingData):
    def __init__(
        self, instId=None|str, timeframe=None|str, lenghts=None|int, 
        load_data_after=None, load_data_before=None
        ):
        super().__init__(key='contracts_prices')
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)
        self.format = MultilineJSONFormatter()


    def get_market_data(self, lenghts=None|int) -> dict:
        # sourcery skip: remove-redundant-if
        if lenghts:
            self.lenghts = lenghts
        if self.load_data_after or self.load_data_before is None:
            return self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after='',
                before='',
                bar=self.timeframe,
                limit=self.lenghts
            )
        elif self.load_data_after and self.load_data_before:
            return self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=self.load_data_after,
                before=self.load_data_before,
                bar=self.timeframe,
                limit=''
            )
        else:
            return self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after='',
                before='',
                bar=self.timeframe,
                limit=300 # 300 Лимит Okx на 1 реквест
            )


    def check_balance(self) -> float:
        result_bal = self.accountAPI.get_account_balance()
        usdt_balance = Decimal(result_bal["data"][0]["details"][0]["availBal"])  # получаем значение ключа ccy по указанному пути
        balance = float(usdt_balance)
        print(f'Баланс: \n {result_bal}\n\n')
        return balance


    # Установка левериджа кросс позиций для отдельного инструмента
    def set_leverage_inst(self) -> None:
        result = self.accountAPI.set_leverage(
            instId=self.instId,
            lever=self.leverage,
            mgnMode=self.mgnMode #cross или isolated
        )
        if result["code"] != "0":
            raise ValueError(f'Set leverage for instrument, code: {result['code']}')
        return self.leverage


    # Установка левериджа для \изолированых позиций для шорт и лонг
    def set_leverage_short_long(self, posSide) -> None:
        result = self.accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            posSide = posSide,
            mgnMode = self.mgnMode
        )
        print(f'Установка левериджа {self.leverage}x, для изолированных лонг {self.instId}: \n{result}\n\n')


    # Установка режима торговли
    def set_trading_mode(self) -> None:
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        print(result)
        
    def check_instrument_info(self, instId:str) -> None:
        result = self.marketDataAPI.get_ticker(instId=instId)
        print(result)


    def check_contract_price(self, save=None|bool) -> None:
        result = self.accountAPI.get_instruments(instType="SWAP")
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)


    def check_contract_price_cache(self, instId:str) -> float:
        result = super().load_message_from_cache()
        return float(next(
                (
                    instrument['ctVal']
                    for instrument in result['data']
                    if instrument['instId'] == instId
                ),
                None,
            ))


    def check_instrument_price(self, instId:str) -> float:
        ticker_data = self.marketDataAPI.get_ticker(instId)
        return float(ticker_data['data'][0]['last'])