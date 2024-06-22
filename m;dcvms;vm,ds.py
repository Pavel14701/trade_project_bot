import yfinance as yf

# Получаем DataFrame
df = yf.download("AAPL", "2023-06-14", "2024-02-14", "1h")
print(df)

df = df.drop(df.index[:1])

print(df)
