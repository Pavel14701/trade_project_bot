#libs
from typing import Optional, Union
import pandas as pd
#api
from api.okx_info import OKXInfoFunctions
from api.okx_info_async import OKXInfoFunctionsAsync
#configs
from configs.load_settings import ConfigsProvider
from risk_manadgment.hist_volat_calc import CalculateHistoricVolatility


class RiskManadgment(CalculateHistoricVolatility):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None,
        entry_price:Union[int, float]=None,posSide:Optional[str]=None,
        slPrice:Union[int, float]=None, data:Optional[pd.DataFrame]=None
        ):
        CalculateHistoricVolatility.__init__(self, timeframe, instId, data)
        user_settings = ConfigsProvider.load_user_configs()
        self.leverage = user_settings['leverage']
        self.risk = user_settings['risk']
        self.entry_price = entry_price
        self.posSide = posSide
        self.instId = instId
        self.slPrice = slPrice
        self.timeframe = timeframe


    def __get_balance_and_contract_price(self):
        instance = OKXInfoFunctions(self.instId)
        self.balance = instance.check_contract_price()
        self.contract_price = instance.check_balance()


    async def __get_balance_and_contract_price_async(self):
        instance = OKXInfoFunctionsAsync(self.instId)
        self.balance = await instance.get_account_balance_async()
        self.contract_price = await instance.check_contract_price_async(instId=self.instId)


    def calculate_pos_size_coef(self, volatility_index:str) -> float:
        coefficients = {
            'long': {'low': 0.98, 'medium': 0.95, 'high': 0.90},
            'short': {'low': 1.02, 'medium': 1.05, 'high': 1.10}
        }
        return self.entry_price * coefficients[self.posSide][volatility_index]


    #Калькулятор стопа
    def calculate_stop_loss(self) -> float:
        volatility = self.calculate_volatility_v2()
        if self.posSide == "long":
            slPrice = self.entry_price - (self.entry_price * volatility / self.leverage)
        elif self.posSide == "short":
            slPrice = self.entry_price + (self.entry_price * volatility / self.leverage)
        return slPrice


    def calculate_pos_size(self, contract_price:float) -> float:
        balance = OKXInfoFunctions().check_balance()
        contract_price = OKXInfoFunctions(self.instId).check_contract_price()
        return ((self.balance * self.leverage * self.risk) / self.slPrice) / contract_price


    async def calculate_pos_size_async(self, contract_price:float) -> float:
        balance = OKXInfoFunctions().check_balance()
        return ((self.balance * self.leverage * self.risk) / self.slPrice) / contract_price