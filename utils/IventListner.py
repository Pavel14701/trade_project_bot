from datasets.RedisCache import RedisCache

class OKXIventListner(RedisCache):
    def __init__(self, instId, orderId):
        super().__init__(instId)
        self.orderId = orderId
        
        
    def create_listner(self, message):
        