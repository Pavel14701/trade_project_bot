import contextlib, time, logging
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from datasets.RedisCache import RedisCache
from datasets.AioRedisCache import AioRedisCache
from datasets.database import AsyncSessionLocal, DataAllDatasets
from datasets.ClassesCreation import Base
from datasets.StatesDB import StateRequest, AsyncStateRequest
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
db.create_classes(Base)



def init_pos_data(message):
    posSide = message['signal']
    slPrice = message['slPrice']
    return posSide, slPrice


class OKXIventListner(RedisCache, AioRedisCache, StateRequest, AsyncStateRequest):
    def __init__(self, Session=None|sessionmaker, AsyncSessionLocal=None|sessionmaker, orderId=str|None):
        super(RedisCache).__init__(key='positions')
        super(AioRedisCache).__init__(key='positions')
        super(StateRequest).__init__(Session)
        super(AsyncStateRequest).__init__(AsyncSessionLocal)
        self.orderId = orderId


    # Если напишем новые стратегии, то действия, которые нужно
    # предпринять нужно сортировать в if elif по message['strategy']
    def create_listner(self):
        try:
            super().subscribe_to_redis_channels()
            while True:
                with contextlib.suppress(Exception):
                    message = super().check_redis_message()
                    self.instId = message['instId']
                    self.timeframe = message['timeframe']
                    self.orderId = PlaceOrders(message['instId'], None, message['signal'], None, message['slPrice'])
                    if positions := super().load_message_from_cache():
                        try:
                            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
                            for index in instIds_match_list:
                                element_b = positions['timeframe'][index]
                                is_match = element_b == self.timeframe
                                if is_match:
                                    search_index = index
                                    break
                            positions['state'][search_index] = message['state']
                            positions['orderId'][search_index] = self.orderId
                            positions['strategy'][search_index] = message['strategy']
                            positions['status'][search_index] = True
                            super().update_state(positions)
                        except Exception:
                            message['orderId'] = self.orderId
                            positions.update(message)
                            super().save_position_state(positions)
                    else:
                        message['orderId'] = self.orderId
                        message = {key: [value] for key, value in message.items()}
                        positions = message
                        super().save_position_state(positions)
                    super().send_redis_command(positions, self.key)
                time.sleep(10)
        except Exception as e:
            logger.error(f" \n{datetime.now().isoformat()} Error create listner:\n{e}")


    async def ivent_reaction(self, msg):
        try:
            if msg['data'][0]:
                data = {
                    'orderId': msg['data'][0]['posId'],
                    'pos': msg['data'][0]['pos'],
                    'instId': msg['data'][0]['instId']
                }
                if data['pos'] == '0':
                    positions = await super().async_load_message_from_cache()
                    instIds_match_list = [i async for i, val in enumerate(positions['instId']) if val == self.instId]
                    async for index in instIds_match_list:
                        element_b = positions['timeframe'][index]
                        is_match = element_b == data['orderId']
                        if is_match:
                            search_index = index
                            break
                    self.instId = data['instId'][search_index]
                    self.timeframe = data['timeframe'][search_index]
                    data['orderId'][search_index] = None
                    data['priceClose'][search_index] = await UserInfo().get_last_price(data['instId'])
                    await super().async_send_redis_command()
                    await super().async_update_state(data)
        except Exception as e:
            logger.error(f" \n{datetime.now().isoformat()} Error ivent reaction:\n{e}")