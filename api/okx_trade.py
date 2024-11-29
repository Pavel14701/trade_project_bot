#libs
from typing import Optional
import pandas as pd
from sqlalchemy.orm import sessionmaker
#functions
from api.okx_info import OKXInfoFunctions
from api.okx_trade_requests import OKXTradeRequests
from datasets.database import DataAllDatasets
#risk-manadgment
from risk_manadgment.risk_manadgment_functions import RiskManadgment
#utils
from datasets.utils.dataframe_utils import create_dataframe, prepare_data_to_dataframe
from baselogs.custom_decorators import log_exceptions
from baselogs.custom_logger import create_logger


logger = create_logger('TradeFunctions')


# !!!Важно, если не вязать IP адрес к ключу,
# у которого есть разрешения на вывод и торговлю(отдельно),
# то он автоматически удалиться через 14 дней.


class PlaceOrders(OKXInfoFunctions, OKXTradeRequests, RiskManadgment, DataAllDatasets):    
    def __init__(
            self, Session:sessionmaker, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None, posSide:Optional[str]=None,
            tpPrice:Optional[float]=None, slPrice=None|float
            ):
        OKXTradeRequests.__init__(self, instId=instId, posSide=posSide, slPrice=slPrice, tpPrice=tpPrice)
        OKXInfoFunctions.__init__(self, instId=instId, timeframe=timeframe)
        RiskManadgment.__init__(self, instId=instId, slPrice=slPrice)
        DataAllDatasets.__init__(self, Session, classes_dict, instId, timeframe)
        self.timeframe, self.instid, self.posSide = timeframe, instId, posSide
        self.tpPrice, self.slPrice = tpPrice, slPrice


    # Создание маркет ордера long с Tp и Sl
    @log_exceptions(logger)
    def place_market_order(self) -> str:
        result = {
            'instID':  self.instId, 'timeframe': self.timeframe,
            'leverage': self.set_leverage_inst(), 'posSide': self.posSide,
            'tpPrice': self.tpPrice, 'slPrice': self.slPrice,
            'posFlag': True
        }
        self.balance, result['balance'] = self.check_balance()
        contract_price, result['contract_price'] = self.check_contract_price_cache(self.instId)
        self.size, result['size'] = self.calculate_pos_size(contract_price)
        result |= self.construct_market_order()
        if not result['order_id']:
            raise ValueError("Unsuccessful order request, error_code = ",result["data"][0], ", Error_message = ", result["data"][0]["sMsg"])
        result['enter_price'] = self.check_position(result['order_id'])
        result['order_id_tp'] = (None if self.tpPrice is None else self.construct_takeprofit_order())
        result['order_id_sl'] = (None if self.slPrice is None else self.construct_stoploss_order())
        self.save_new_order_data(result)
        return str(result['order_id'])

        
        
    # Размещение лимитного ордера
    @log_exceptions(logger)
    def place_limit_order(self, price:float) -> str:
        result = {
            'instID':  self.instId, 'timeframe': self.timeframe,
            'leverage': self.set_leverage_inst(), 'posSide': self.posSide,
            'tpPrice': self.tpPrice, 'slPrice': self.slPrice,
            'enter_price': price, 'posFlag': False,
        }
        self.balance, result['balance'] = self.check_balance()
        contract_price, result['contract_price'] = self.check_contract_price_cache(self.instId)
        self.size, result['size'] = self.calculate_pos_size(contract_price)
        result['result'], result['order_id'], outTime = self.costruct_limit_order(price)
        if not result['order_id']:
            raise ValueError('Unsuccessful order request, error_code = ',result["data"][0], ', Error_message = ', result["data"][0]["sMsg"])
        result['order_id_tp']=(None if self.tpPrice is None else self.construct_takeprofit_order())
        result['order_id_sl'] = (None if self.slPrice is None else self.construct_stoploss_order())
        self.save_new_order_data(result)
        return str(result['order_id'])


    @log_exceptions(logger)
    def get_current_chart_data(self) -> pd.DataFrame:
        result = self.get_market_data()
        if 'data' not in result or len(result["data"]) <= 0:
            raise ValueError("Данные отсутствуют или неполные")
        data_list = prepare_data_to_dataframe(result)
        return create_dataframe(data_list)