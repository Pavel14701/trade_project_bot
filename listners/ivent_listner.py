#libs
import contextlib, time
from typing import Optional
#database
from datasets.states_db import StateRequest
from datasets.async_states_db import AsyncStateRequest
#cache
from cache.redis_cache import RedisCache
from cache.aioredis_cache import AioRedisCache
#functions
from api.okx_trade import PlaceOrders
from api.okx_info_async import OKXInfoFunctionsAsync
#utils
from baselogs.custom_logger import create_logger
logger = create_logger('IventListner')





class OKXIventListner(RedisCache, AioRedisCache):
    def __init__(self, orderId:Optional[str]=None):
        RedisCache.__init__(self, key='positions')
        AioRedisCache.__init__(self, key='positions')
        self.orderId = orderId


    def __find_index(self, positions:dict) -> int:
        try:
            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
            for index in instIds_match_list:
                element_b = positions['timeframe'][index]
                is_match = element_b == self.timeframe
                if is_match:
                    search_index = index
                    break
            return search_index
        except Exception:
            return None


    def __update_pos_if(self, positions:dict, message:dict):
        if search_index := self.__find_index(positions):
            positions['state'][search_index], positions['orderId'][search_index] = message['state'], self.orderId
            positions['strategy'][search_index], positions['status'][search_index] = message['strategy'], True
            StateRequest(self.instId, self.timeframe, self.strategy).update_state(positions)
        else:
            message['orderId'] = self.orderId
            positions |= message
            StateRequest(self.instId, self.timeframe).save_position_state(positions)
        return positions


    def __update_pos_else(self, message:dict):
        message['orderId'] = self.orderId
        message = {key: [value] for key, value in message.items()}
        positions = message
        StateRequest(self.instId, self.timeframe).save_position_state(positions)
        return positions


    def create_listner(self):
        self.subscribe_to_redis_channels()
        while True:
            with contextlib.suppress(Exception):
                try:
                    message = self.check_redis_message()
                    self.instId, self.timeframe, self.strategy  = message['instId'], message['timeframe'], message['strategy']
                    self.orderId = PlaceOrders(message['instId'], None, message['signal'],\
                        None, message['slPrice']).place_market_order()
                    if positions := self.load_message_from_cache():
                        positions = self.__update_pos_if(positions, message)
                    else:
                        positions = self.__update_pos_else(message)
                    self.send_redis_command(positions, self.key)
                except Exception as e:
                    print(e)
                    logger.error(f'Error:{e}')
                time.sleep(10)


    async def ivent_reaction(self, msg:dict) -> None:
        try:
            if msg['data'][0]:
                data = {'orderId': msg['data'][0]['posId'], 'pos': msg['data'][0]['pos'],
                        'instId': msg['data'][0]['instId']}
                if data['pos'] == '0':
                    positions = await self.async_load_message_from_cache()
                    if search_index := await self.__find_index_async(positions):
                        await self.__add_db_close_data(data, search_index)
        except Exception as e:
            logger.error(f'Error:{e}')


    async def __add_db_close_data(self, data:dict, search_index:int) -> None:
        self.instId, self.timeframe  = data['instId'][search_index], data['timeframe'][search_index]
        data['orderId'][search_index] = None
        data['priceClose'][search_index] = await OKXInfoFunctionsAsync().get_last_price(self.instId)
        await self.async_send_redis_command()
        await AsyncStateRequest(self.instId, self.timeframe).save_position_state_async(data)


    async def __find_index_async(self, positions:dict) -> int:
        try:
            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
            for index in instIds_match_list:
                element_b = positions['timeframe'][index]
                is_match = element_b == self.timeframe
                if is_match:
                    search_index = index
                    break
            return search_index
        except Exception:
            return None
