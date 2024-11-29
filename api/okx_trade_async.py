#libs
from typing import Optional, Union
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
#Api
from api.okx_info_async import OKXInfoFunctionsAsync
from api.okx_trade_requests_async import OKXTradeRequestsAsync
#risk-manadgment
from risk_manadgment.risk_manadgment_functions import RiskManadgment
#database
from datasets.database_async import DataAllDatasetsAsync
#utils
from datasets.utils.dataframe_utils_async import create_dataframe_async, prepare_data_to_dataframe_async
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import log_exceptions_async
logger = create_logger('TradeFunctionsAsync')


# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'


class PlaceOrdersAsync(OKXTradeRequestsAsync, RiskManadgment, OKXInfoFunctionsAsync, DataAllDatasetsAsync):    
    def __init__(self, Session:AsyncSession, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None, posSide:Optional[str]=None, tpPrice:Union[float, int]=None, slPrice:Union[float, int]=None):
        OKXTradeRequestsAsync.__init__(self, instId=instId, posSide=posSide, slPrice=slPrice, tpPrice=tpPrice)
        OKXInfoFunctionsAsync.__init__(self, instId=instId, timeframe=timeframe)
        RiskManadgment.__init__(self, instId=instId, slPrice=slPrice)
        DataAllDatasetsAsync.__init__(self, Session, classes_dict, instId, timeframe)
        self.instid, self.timeframe, self.posSide = instId, timeframe, posSide
        self.tpPrice, self.tpPrice = tpPrice, slPrice

    # Создание маркет ордера long с Tp и Sl
    @log_exceptions_async(logger)
    async def place_market_order_async(self) -> str:
        result = {
            'instID':  self.instId, 'timeframe': self.timeframe,
            'leverage': await self.set_leverage_inst(), 'posSide': self.posSide,
            'tpPrice': self.tpPrice, 'slPrice': self.slPrice, 'posFlag': True
        }
        self.balance, result['balance'] = await self.get_account_balance()
        result['contract_price'] = await self.check_contract_price_cache_async(self.instId)
        self.size, result['size'] = await self.calculate_pos_size_async(result['contract_price'])
        result |= await self.construct_market_order()
        if not result['order_id']:
            raise ValueError('Unsuccessful order request, error_code = ',result["data"][0], ', Error_message = ', result["data"][0]["sMsg"])
        result['enter_price'] = await self.check_position(result['order_id'])
        result['order_id_tp'] = (None if self.tpPrice is None else await self.construct_takeprofit_order())
        result['order_id_sl'] = (None if self.slPrice is None else await self.construct_stoploss_order())
        await self.save_new_order_data_async(result)
        return result['order_id']
        
        
    # Размещение лимитного ордера
    @log_exceptions_async(logger)
    async def place_limit_order(self, price:float) -> str:
        result = {
            'instID':  self.instId, 'timeframe': self.timeframe,
            'leverage': await self.set_leverage_inst(), 'posSide': self.posSide,
            'tpPrice': self.tpPrice, 'slPrice': self.slPrice,
            'enter_price': price, 'posFlag': False,
        }
        self.balance, result['balance'] = await self.get_account_balance()
        contract_price, result['contract_price'] = await self.check_contract_price_cache_async(self.instId)
        self.size, result['size'] = await self.calculate_pos_size_async(contract_price)
        result['result'], result['order_id'], outTime = await self.construct_limit_order(price)
        if not result['order_id']:
            raise ValueError('Unsuccessful order request, error_code = ',result["data"][0], ', Error_message = ', result["data"][0]["sMsg"])
        result['order_id_tp'] = (None if self.tpPrice is None else await self.construct_takeprofit_order())
        result['order_id_sl'] = (None if self.slPrice is None else await self.construct_stoploss_order())
        await self.save_new_order_data_async(result)
        return result['order_id']


    async def get_current_chart_data(self) -> pd.DataFrame:
        result = await self.get_candlesticks()
        if 'data' not in result or len(result["data"]) <= 0:
            raise ValueError("Данные отсутствуют или неполные")
        data_list = await prepare_data_to_dataframe_async(result)
        return await create_dataframe_async(data_list)