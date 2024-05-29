class RiskMenedgment:
    def __init__(self, balance, leverage, risk, entry_price, posSide, volatility):
        self.balance = balance
        self.leverage = leverage
        self.risk = risk
        self.entry_price = entry_price
        self.posSide = posSide
        self.volatility = volatility

    def calculate_pos_size(self):
        x = 10000 # ваш капитал
        L = 20 # леверидж
        risk = 0.03 # риск
        y = 50 # цена входа в сделку
        direction = "long" # направление сделки ("long" или "short")
        volatility = "medium" # волатильность базового актива ("low", "medium" или "high")

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
        slPrice = self.enter_price * coefficients[self.posSide][volatility]
        # Рассчитываем размер позиции
        P = (self.balance * self.leverage * self.risk) / slPrice
        #   Выводим результаты
        print(f"Стоп-лос: {slPrice:.2f}")
        print(f"Размер позиции: {P:.2f}")