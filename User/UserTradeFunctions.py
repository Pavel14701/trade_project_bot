import logging
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
from datasets.database import DataAllDatasets, Base
from datasets.database import Session
from User.LoadSettings import LoadUserSettingData
from User.TradeRequests import OKXTradeRequests
from User.UserInfoFunctions import UserInfo
from utils.RiskManagment import RiskManadgment
from utils.DataFrameUtils import create_dataframe, prepare_data_to_dataframe

# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'
bd = DataAllDatasets(Session=Session)
TradeUserData = bd.create_TradeUserData(Base)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('trade_functions.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PlaceOrders(OKXTradeRequests, RiskManadgment, UserInfo, LoadUserSettingData):    
    def __init__(
            self,
            instId=None|str, posSide=None|str, tpPrice=None|float,
            slPrice=None|float
            ):
        super().__init__(instId, posSide, tpPrice, slPrice)

        
    # Создание маркет ордера long с Tp и Sl
    def place_market_order(self) -> str:
        # sourcery skip: extract-method, merge-dict-assign, switch
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': super().set_leverage_inst(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'posFlag': True
            }
            self.balance, result['balance'] = super().check_balance()
            contract_price, result['contract_price'] = super().check_contract_price_cache(self.instId)
            self.size, result['size'] = super().calculate_pos_size(contract_price)
            result |= super().construct_market_order()
            if result['order_id'] is not None:
                result['enter_price'] = super().check_position(result['order_id'])
                if self.tpPrice is None:
                    result['order_id_tp'] = None
                else:
                    result['order_id_tp'] = super().construct_takeprofit_order()
                if self.slPrice is None:
                    result['order_id_sl'] = None
                else:
                    result['order_id_sl'] = super().construct_stoploss_order()
                with Session() as session:
                    prepare_data_order_to_commit(session, result)
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0], ", Error_message = ", result["data"][0]["sMsg"])
            return result['order_id']
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place market order:\n{e}")
        
        
    # Размещение лимитного ордера
    def place_limit_order(self, price:float) -> str:
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': super().set_leverage_inst(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'enter_price': price,
                'posFlag': False,
            }
            self.balance, result['balance'] = super().check_balance()
            contract_price, result['contract_price'] = super().check_contract_price_cache(self.instId)
            self.size, result['size'] = super().calculate_pos_size(contract_price)
            # limit order
            result, order_id, outTime = super().construct_limit_order(price)
            if self.tpPrice is None:
                result['order_id_tp'] = None
            else:
                result['order_id_tp'] = super().construct_takeprofit_order()
            if self.slPrice is None:
                result['order_id_sl'] = None
            else:
                result['order_id_tp'] = super().construct_takeprofit_order()
            if order_id is not None:
                with Session() as session:
                    prepare_data_order_to_commit(session, result)  
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])
            return order_id
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place limit order:\n{e}")


    def get_current_chart_data(self) -> pd.Dataframe:
        try:
            result = super().get_market_data()
            if 'data' in result and len(result["data"]) > 0:
                data_list = prepare_data_to_dataframe(result)
                return create_dataframe(data_list)
            else:
                print("Данные отсутствуют или неполные")
        except Exception as e:
            logger.error(f" \n{datetime.datetime.now().isoformat()} Error get current chart data:\n{e}")



def prepare_data_order_to_commit(session:sessionmaker, result:dict) -> None:
    order_id = TradeUserData(
        order_id=result['order_id'],
        status=result['posFlag'],
        order_volume=result['size'],
        tp_order_volume=result['size'],
        sl_order_volume=result['size'],
        balance=result['balance'],
        instrument=result['instId'],
        leverage=result['leverage'],
        side_of_trade=result['posSide'],
        enter_price=result['enter_price'],
        time=result['outTime'],
        tp_order_id=result['order_id_tp'],
        tp_price=result['tpPrice'],
        sl_order_id=result['order_id_sl'],
        sl_price=result['slPrice']
    )
    try:
        session.add(order_id)
        session.commit()
    except Exception as e:
        session.rollback()
        if result['posFlag']:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error save market data in db:\n{e}")
        else:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error save limit data in db:\n{e}")
    finally:
        session.close()
