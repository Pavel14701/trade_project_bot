import contextlib, time
from datasets.RedisCache import RedisCache
from User.UserTradeFunctions import PlaceOrders

def init_pos_data(message):
    posSide = message['signal']
    slPrice = message['slPrice']
    return posSide, slPrice
    

class OKXIventListner(RedisCache):
    def __init__(self, instId:str, orderId=None):
        super().__init__(instId, key='positions')
        self.orderId = orderId
        
        
    def create_listner(self):
        super().subscribe_to_redis_channel()
        while True:
            with contextlib.suppress(Exception):
                message = super().check_redis_message()
                posSide, slPrice = init_pos_data(message)
                self.orderId = PlaceOrders(self.instId, None, posSide, None, slPrice)
                messages = super().load_message_from_cache()
                if messages is not None:
                    messages.append(self.orderId)
                    super().send_redis_command(messages)
                else:
                    super().send_redis_command(list(self.orderId))
                time.sleep(1)