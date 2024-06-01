class RiskMenedgment:
    def __init__(self, balance, leverage, risk, entry_price, posSide, volatility, data_source):
        self.balance = balance
        self.leverage = leverage
        self.risk = risk
        self.entry_price = entry_price
        self.posSide = posSide
        self.volatility = volatility
        self.data_source = self.data_source # OKX or Yfinance

    def calculate_pos_size(self):
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
        slPrice = self.enter_price * coefficients[self.posSide][self.volatility]
        # Рассчитываем размер позиции
        P = (self.balance * self.leverage * self.risk) / slPrice
        #   Выводим результаты
        print(f"Стоп-лос: {slPrice:.2f}")
        print(f"Размер позиции: {P:.2f}")