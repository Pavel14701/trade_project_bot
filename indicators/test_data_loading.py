import yfinance as yf

class LoadDataFromYF:
    @staticmethod
    def load_test_data(ticker, start, end, timeframe):
        # Загружаем данные по акциям Apple
        data = yf.download(ticker, start, end, interval=timeframe)
        return data
    

