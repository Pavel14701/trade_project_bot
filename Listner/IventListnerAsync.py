#dataset
from datasets.AioRedisCache import AioRedisCache
from datasets.AsyncStatesDB import AsyncStateRequest
#funtions
from User.UserTradeFunctions import PlaceOrders
from User.UserInfoFunctionsAsync import UserInfoAsync
#utils
from utils.CustomLogger import create_logger
import contextlib, time
#logger
logger = create_logger('IventListner')





def init_pos_data(message):
    posSide = message['signal']
    slPrice = message['slPrice']
    return posSide, slPrice


class OKXIventListner(AioRedisCache, AsyncStateRequest):
    def __init__(self, orderId=str|None):
        AioRedisCache.__init__(key='positions')
        AsyncStateRequest.__init__()
        self.orderId = orderId


    async def create_listner(self):
        self.async_subscribe_to_redis_channels()
        while True:
            try:
                with contextlib.suppress(Exception):
                    message = await self.async_check_redis_message()
                    self.instId = message['instId']
                    self.timeframe = message['timeframe']
                    self.orderId = PlaceOrders(message['instId'], None, message['signal'], None, message['slPrice'])
                    if positions := await self.async_load_message_from_cache():
                        try:
                            instIds_match_list = [i async for i, val in enumerate(positions['instId']) if val == self.instId]
                            async for index in instIds_match_list:
                                element_b = positions['timeframe'][index]
                                is_match = element_b == self.timeframe
                                if is_match:
                                    search_index = index
                                    break
                            positions['state'][search_index] = message['state']
                            positions['orderId'][search_index] = self.orderId
                            positions['strategy'][search_index] = message['strategy']
                            positions['status'][search_index] = True
                            await self.update_state_async(positions)
                        except ValueError:
                            message['orderId'] = self.orderId
                            positions.update(message)
                            self.save_position_state_async(positions)
                    else:
                        message['orderId'] = self.orderId
                        message = {key: [value] for key, value in message.items()}
                        positions = message
                        self.save_position_state_async(positions)
                    await self.async_send_redis_command(positions, self.key)
                time.sleep(10)
            except Exception as e:
                logger.error(f'Error:{e}')



    async def ivent_reaction(self, msg):
        try:
            if msg['data'][0]:
                data = {
                    'orderId': msg['data'][0]['posId'],
                    'pos': msg['data'][0]['pos'],
                    'instId': msg['data'][0]['instId']
                }
                if data['pos'] == '0':
                    positions = await self.async_load_message_from_cache()
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
                    data['priceClose'][search_index] = await UserInfoAsync().get_last_price_async(self.instId)
                    await self.async_send_redis_command()
                    await self.update_state_async(data)
        except Exception as e:
            logger.error(f'Error:{e}')