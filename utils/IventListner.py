import contextlib, time
from datasets.RedisCache import RedisCache
from User.UserTradeFunctions import PlaceOrders

def init_pos_data(message):
    posSide = message['signal']
    slPrice = message['slPrice']
    return posSide, slPrice
    


class OKXIventListner(RedisCache):
    def __init__(self, instId, orderId=None):
        super().__init__(instId)
        self.orderId = orderId
        
        
    def create_listner(self):
        super().subscribe_to_redis_channel()
        while True:
            with contextlib.suppress(Exception):
                message = super().check_redis_message()
                if message['instId'] == self.instId:
                    posSide, slPrice = init_pos_data(message)
                    self.orderId = PlaceOrders(self.instId, None, posSide, None, slPrice)
                super().send_redis_command(self.orderId)
                time.sleep(1)