from User.LoadSettings import LoadUserSettingData
class RiskManadgment(LoadUserSettingData):
    def __init__(self, balance=None|int, entry_price=None|str, posSide=None|str, 
                 instId=None|str, slPrice=None|float, timeframe=None|str):
        super().__init__()
        self.balance = balance
        self.entry_price = entry_price
        self.posSide = posSide
        self.instId = instId
        self.slPrice = slPrice
        self.timeframe = timeframe
        

    def calculate_pos_size(self, volatility:float):
        coefficients = {
            "long": {
                "low": 0.98,
                "medium": 0.95,
                "high": 0.90
            },
            "short": {
                "low": 1.02,
                "medium": 1.05,
                "high": 1.10
            }
        }
        # Рассчитываем стоп-лос
        return self.enter_price * coefficients[self.posSide][volatility]


    #Калькулятор стопа
    def calculate_stop_loss(self, volat):
        print(volat)
        if self.posSide == "long":
            # Рассчитываем стоп-лос
            slPrice = self.entry_price - (self.entry_price * volat[f'{self.instId}_{self.timeframe}'] / self.leverage)
        elif self.posSide == "short":
            # Рассчитываем стоп-лос
            slPrice = self.entry_price + (self.entry_price * volat[f'{self.instId}_{self.timeframe}'] / self.leverage)
        # Рассчитываем размер позиции
        return slPrice


    def calculate_pos_size(self):
        return (self.balance * self.leverage * self.risk) / self.slPrice