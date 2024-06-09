import yfinance as yf


class LoadDataFromYF:
    """Summary:
    Class for loading test data from Yahoo Finance.

    Explanation:
    This class provides a static method to load test data for a specified ticker symbol, start and end dates, and timeframe using Yahoo Finance API.

    Args:
    - ticker: The stock ticker symbol.
    - start: The start date for the data.
    - end: The end date for the data.
    - timeframe: The timeframe for the data (e.g., '1d' for daily).

    Returns:
    - The loaded test data.
    """

    @staticmethod
    def load_test_data(ticker, start, end, timeframe):
        """Summary:
        Load test data from Yahoo Finance.

        Explanation:
        This static method downloads historical data for a specified stock ticker symbol, start and end dates, and timeframe using the Yahoo Finance API.

        Args:
        - ticker: The stock ticker symbol.
        - start: The start date for the data.
        - end: The end date for the data.
        - timeframe: The timeframe for the data (e.g., '1d' for daily).

        Returns:
        - The loaded test data.
        """
        # sourcery skip: inline-immediately-returned-variable
        data = yf.download(ticker, start, end, interval=timeframe)
        return data


data = LoadDataFromYF.load_test_data("AAPL", start="2023-06-14", end="2024-02-14", timeframe="1h")
print(data)
print(type(data))
