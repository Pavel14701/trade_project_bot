import yfinance as yf
import pandas as pd

# Получаем DataFrame
df = yf.download("AAPL", "2023-06-14", "2024-02-14", "1D")
print(df)
df = df.drop(df.index[:1])
print(df)
a = yf.download("AAPL", "2024-02-14", "2024-02-15", "1D")
print(a)
df = pd.concat([df, a])
print(df)
