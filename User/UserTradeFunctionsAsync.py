import logging
from typing import Optional, Union
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime
from datasets.DataBaseAsync import DataAllDatasetsAsync
from User.TradeRequestsAsync import OKXTradeRequestsAsync
from User.UserInfoFunctionsAsync import UserInfoAsync
from utils.RiskManagment import RiskManadgment
from utils.DataFrameUtils import create_dataframe_async, prepare_data_to_dataframe_async

# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('trade_functions.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PlaceOrdersAsync(OKXTradeRequestsAsync, RiskManadgment, UserInfoAsync, DataAllDatasetsAsync):    
    def __init__(
            self, Session:sessionmaker,
            instId:Optional[str]=None, posSide:Optional[str]=None, tpPrice:Union[float, int]=None,
            slPrice:Union[float, int]=None
            ):
        super(OKXTradeRequestsAsync).__init__(instId=instId, posSide=posSide, slPrice=slPrice, tpPrice=tpPrice)
        super(UserInfoAsync).__init__(instId=instId)
        super(RiskManadgment).__init__(instId=instId, slPrice=slPrice)
        super(DataAllDatasetsAsync).__init__()
        self.instid = instId
        self.Session = Session
        self.posSide = posSide
        self.tpPrice = tpPrice
        self.slPrice = slPrice


    # Создание маркет ордера long с Tp и Sl
    async def place_market_order_async(self) -> str:
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': await self.set_leverage_inst_async(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'posFlag': True
            }
            self.balance, result['balance'] = await self.get_account_balance_async()
            contract_price, result['contract_price'] = await self.check_contract_price_cache_async(self.instId)
            self.size, result['size'] = await self.calculate_pos_size_async(contract_price)
            result |= await self.construct_market_order_async()
            if result['order_id'] is not None:
                result['enter_price'] = await self.check_position_async(result['order_id'])
                if self.tpPrice is None:
                    result['order_id_tp'] = None
                else:
                    result['order_id_tp'] = await self.construct_takeprofit_order_async()
                if self.slPrice is None:
                    result['order_id_sl'] = None
                else:
                    result['order_id_sl'] = await self.construct_stoploss_order_async()
                await self.save_new_order_data_async(result)
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0], ", Error_message = ", result["data"][0]["sMsg"])
            return result['order_id']
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place market order:\n{e}")
        
        
    # Размещение лимитного ордера
    async def place_limit_order(self, price:float) -> str:
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': await self.set_leverage_inst_async(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'enter_price': price,
                'posFlag': False,
            }
            self.balance, result['balance'] = await self.get_account_balance_async()
            contract_price, result['contract_price'] = await self.check_contract_price_cache_async(self.instId)
            self.size, result['size'] = await self.calculate_pos_size_async(contract_price)
            # limit order
            result, order_id, outTime = await self.construct_limit_order_async(price)
            if self.tpPrice is None:
                result['order_id_tp'] = None
            else:
                result['order_id_tp'] = await self.construct_takeprofit_order_async()
            if self.slPrice is None:
                result['order_id_sl'] = None
            else:
                result['order_id_tp'] = await self.construct_takeprofit_order_async()
            if order_id is not None:
                await self.save_new_order_data_async(result)
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])
            return order_id
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place limit order:\n{e}")


    async def get_current_chart_data(self) -> pd.DataFrame:
        try:
            result = await self.get_candlesticks_async()
            if 'data' in result and len(result["data"]) > 0:
                data_list = await prepare_data_to_dataframe_async(result)
                return await create_dataframe_async(data_list)
            else:
                print("Данные отсутствуют или неполные")
        except Exception as e:
            logger.error(f" \n{datetime.datetime.now().isoformat()} Error get current chart data:\n{e}")