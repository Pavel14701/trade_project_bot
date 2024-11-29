#libs
import contextlib, time
from typing import Optional
#datasets
from datasets.async_states_db import AsyncStateRequest
#cache
from cache.aioredis_cache import AioRedisCache
#funtions
from api.okx_info_async import OKXInfoFunctionsAsync
from api.okx_trade_async import PlaceOrdersAsync
#utils
from baselogs.custom_logger import create_logger


logger = create_logger('IventListner')


class OKXIventListnerAsync(AioRedisCache, AsyncStateRequest):
    def __init__(self, orderId:Optional[str]=None):
        AioRedisCache.__init__(key='positions')
        AsyncStateRequest.__init__()
        self.orderId = orderId


    async def __find_index(self, positions:dict) -> int:
        instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
        for index in instIds_match_list:
            element_b = positions['timeframe'][index]
            is_match = element_b == self.timeframe
            if is_match:
                search_index = index
                break
        return search_index


    async def __update_pos_if(self, positions:dict, message:dict) -> dict:
        try:
            search_index = self.__find_index(positions)
            positions['state'][search_index], positions['orderId'][search_index]  = message['state'], self.orderId
            positions['strategy'][search_index], positions['status'][search_index] = message['strategy'], True
            await self.update_state_async(positions)
            return positions
        except ValueError:
            message['orderId'] = self.orderId
            positions |= message
            self.save_position_state_async(positions)
            return positions


    async def __update_pos_else(self, message:dict):
        message['orderId'] = self.orderId
        message = {key: [value] for key, value in message.items()}
        positions = message
        self.save_position_state_async(positions)
        return positions


    async def create_listner(self) -> None:
        self.async_subscribe_to_redis_channels()
        while True:
            try:
                with contextlib.suppress(Exception):
                    message = await self.async_check_redis_message()
                    self.instId, self.timeframe = message['instId'], message['timeframe']
                    self.orderId = await PlaceOrdersAsync(message['instId'], None, message['signal'],\
                        None, message['slPrice']).place_market_order_async()
                    if positions := await self.async_load_message_from_cache():
                        positions = await self.__update_pos_if(positions, message)
                    else:
                        positions = await self.__update_pos_else(message)
                    await self.async_send_redis_command(positions, self.key)
                # возможно нужно использовать слип из асинцио
                time.sleep(10)
            except Exception as e:
                logger.error(f'Error:{e}')



    async def ivent_reaction(self, msg:dict) -> None:
        try:
            if msg['data'][0]:
                data = {'orderId': msg['data'][0]['posId'], 'pos': msg['data'][0]['pos'],
                        'instId': msg['data'][0]['instId']}
                if data['pos'] == '0':
                    positions = await self.async_load_message_from_cache()
                    search_index = await self.__find_index(positions)
                    await self.__add_db_close_data(data, search_index)
        except Exception as e:
            logger.error(f'Error:{e}')


    async def __add_db_close_data(self, data:dict, search_index:int) -> None:
        self.instId, self.timeframe  = data['instId'][search_index], data['timeframe'][search_index]
        data['orderId'][search_index] = None
        data['priceClose'][search_index] = await OKXInfoFunctionsAsync().get_last_price(self.instId)
        await self.async_send_redis_command()
        await self.update_state_async(data)