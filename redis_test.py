import redis

# Создание клиента Redis
r = redis.Redis('127.0.0.1', port=6379, db=0)

# Выполнение команды PING
response = r.ping()

# Вывод результата
print("Response from Redis server:", response)
