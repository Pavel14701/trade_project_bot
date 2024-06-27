from datasets.StatesDB import StateRequest
from User.UserTradeFunctions import PlaceOrders
from datasets.RedisCache import RedisCache
from sqlalchemy.orm import sessionmaker

class States(StateRequest, RedisCache):
    def __init__(self, instId: str, timeframe:str, Session:sessionmaker, channel:str):
        super().__init__(instId, timeframe, Session, channel)
        
        
        
    def load_position_state(self):
        load_data = super().check_state()
        if load_data is None or load_data['POSITION'] is None:
            position_state = None
        elif load_data['POSITION'] == 'long':
            position_state = 'long'
        elif load_data['POSITION'] == 'short':
            position_state =='short'
        return position_state
    
    
    def open_position(self):
        message = super().load_message_from_cache()
        position = str(message['signal'])
        slPrice = float(message['slPrice'])
        adx_trend = int(message['trend_strenghts'])
        volume = PlaceOrders.calculate_posSize(self.risk, self.leverage, slPrice)
        if adx_trend >= 30:
                trade = PlaceOrders(self.instId, volume, position, self.leverage,
                                    self.risk, None, slPrice, self.mgnMode)
                trade.place_market_order()
                super().save_position_state(position, volume)
        else:
            pass
        
        
        
    def trailing_stop_loss(self):
        message = super().load_message_from_cache()
        slPrice = float(message['slPrice'])
        
        
        
    
    
        