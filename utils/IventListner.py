import contextlib, time
import logging
from datetime import datetime
from datasets.RedisCache import RedisCache
from datasets.AioRedisCache import AioRedisCache
from datasets.database import AsyncSessionLocal, Base, DataAllDatasets
from datasets.StatesDB import StateRequest
from User.UserTradeFunctions import PlaceOrders
from User.UserInfoFunctions import UserInfo
from utils.LoggingFormater import MultilineJSONFormatter


logger = logging.getLogger('websocket')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("listner.log")
file_handler.setFormatter(MultilineJSONFormatter())
handler = logging.StreamHandler()
handler.setFormatter(MultilineJSONFormatter())
logger.addHandler(file_handler)
logger.addHandler(handler)


db = DataAllDatasets(AsyncSessionLocal)
TradeUserData = db.create_TradeUserData(Base)


def init_pos_data(message):
    posSide = message['signal']
    slPrice = message['slPrice']
    return posSide, slPrice


class OKXIventListner(RedisCache, AioRedisCache, StateRequest):
    def __init__(self, instId:str, timeframe:str, orderId=None):
        super().__init__(instId, timeframe, key='positions')
        self.orderId = orderId


    def create_listner(self):
        try:
            super().subscribe_to_redis_channels()
            while True:
                with contextlib.suppress(Exception):
                    message = super().check_redis_message()
                    posSide, slPrice = init_pos_data(message)
                    self.orderId = PlaceOrders(self.instId, None, posSide, None, slPrice)
                    super().set_state(self.orderId, self.instId, posSide)
                    messages = super().load_message_from_cache()
                    logger.info(f'\n{datetime.datetime.now().isoformat()} Message: {messages}')
                    if messages is not None:
                        messages.append(self.orderId)
                        super().send_redis_command(messages, self.key)
                    else:
                        super().send_redis_command(list(self.orderId))
                time.sleep(5)
        except Exception as e:
            logger.error(f" \n{datetime.now().isoformat()} Error create listner:\n{e}")
    
# Задача трёх тел процесс, redis и sql 
# Тут какая - то ёбань
    async def ivent_reaction(self, msg):
        try:
            if msg['data']:
                data = {
                    'orderId': msg['data']['posId'],
                    'instId': msg['data']['instId'],
                    'pos': msg['data']['pos']
                }
                message = await super().async_load_message_from_cache()
                async for GetOrderId in message:
                    if GetOrderId == data['orderId'] and data['pos'] == 0:
                        info = UserInfo()
                        # Нужна асинк версия
                        data['priceClose'] = await info.check_instrument_price
                        await super().async_set_state('None', data['orderId'])
                        await super().save_none_state()
            else:
                logger.info(f'\n{datetime.now().isoformat()} Event:')
                logger.info(msg)
        except Exception as e:
            logger.error(f" \n{datetime.now().isoformat()} Error ivent reaction:\n{e}")
                    