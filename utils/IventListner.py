import contextlib, time
from datasets.RedisCache import RedisCache

class OKXIventListner(RedisCache):
    def __init__(self, instId, orderId):
        super().__init__(instId)
        self.orderId = orderId
        
        
    def create_listner(self):
        super().subscribe_to_redis_channel()
        while True:
            with contextlib.suppress(Exception):
                super().check_redis_message()
                
                super().send_redis_command(command)
                time.sleep(1)