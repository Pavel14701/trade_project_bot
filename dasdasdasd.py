import pandas as pd
import redis
import pickle
import yfinance as yf

# Создайте DataFrame
df = yf.download("AAPL", "2024-01-14", "2024-02-14", "1D")

# Сериализуйте DataFrame в формат Pickle
pickled_df = pickle.dumps(df)

# Соединитесь с Redis
r = redis.Redis(host='localhost', port=6379)

# Сохраните сериализованный DataFrame в Redis
r.set('my_dataframe', pickled_df)

# Получите сериализованный DataFrame из Redis
loaded_df = pickle.loads(r.get('my_dataframe'))

# Преобразуйте его обратно в DataFrame
loaded_df = pd.DataFrame(loaded_df)

print(loaded_df)
print(df.equals(loaded_df)) 
