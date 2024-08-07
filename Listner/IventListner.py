import contextlib, time
from typing import Optional
from datasets.RedisCache import RedisCache
from datasets.AioRedisCache import AioRedisCache
from datasets.StatesDB import StateRequest
from datasets.AsyncStatesDB import AsyncStateRequest
from User.UserTradeFunctions import PlaceOrders
from User.UserInfoFunctionsAsync import UserInfoAsync
from utils.CustomLogger import create_logger
logger = create_logger('IventListner')





class OKXIventListner(RedisCache, AioRedisCache):
    def __init__(self, orderId:Optional[str]=None):
        RedisCache.__init__(key='positions')
        AioRedisCache.__init__(key='positions')
        self.orderId = orderId


    def create_listner(self):
        self.subscribe_to_redis_channels()
        while True:
            try:
                with contextlib.suppress(Exception):
                    message = self.check_redis_message()
                    self.instId = message['instId']
                    self.timeframe = message['timeframe']
                    self.strategy = message['strategy']
                    self.orderId = PlaceOrders(message['instId'], None, message['signal'],\
                        None, message['slPrice']).place_market_order()
                    if positions := self.load_message_from_cache():
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
                            StateRequest(self.instId, self.timeframe, self.strategy).update_state(positions)
                        except ValueError:
                            message['orderId'] = self.orderId
                            positions.update(message)
                            StateRequest(self.instId, self.timeframe).save_position_state(positions)
                    else:
                        message['orderId'] = self.orderId
                        message = {key: [value] for key, value in message.items()}
                        positions = message
                        StateRequest(self.instId, self.timeframe).save_position_state(positions)
                    self.send_redis_command(positions, self.key)
                time.sleep(10)
            except Exception as e:
                logger.error(f'Error:{e}')


    async def ivent_reaction(self, msg):
        try:
            if msg['data'][0]:
                pos_data = {
                    'orderId': msg['data'][0]['posId'],
                    'pos': msg['data'][0]['pos'],
                    'instId': msg['data'][0]['instId'],
                    'strategy': msg['data'][0]['strategy']
                }
                if pos_data['pos'] == '0':
                    positions = await self.async_load_message_from_cache()
                    instIds_match_list = [i async for i, val in enumerate(positions['instId']) if val == self.instId]
                    async for index in instIds_match_list:
                        element_b = positions['timeframe'][index]
                        is_match = element_b == pos_data['orderId']
                        if is_match:
                            search_index = index
                            break
                    self.instId = pos_data['instId'][search_index]
                    self.timeframe = pos_data['timeframe'][search_index]
                    pos_data['orderId'][search_index] = None
                    pos_data['priceClose'][search_index] = await UserInfoAsync().get_last_price_async(pos_data['instId'])
                    await self.async_send_redis_command()
                    await AsyncStateRequest(pos_data['instId'], pos_data['timeframe'],\
                        pos_data['strategy']).update_state_async(pos_data)
        except Exception as e:
            logger.error(f'Error:{e}')