import requests
import time
import hashlib
import hmac
import base64

# Ваши данные API
api_key = '0a485d9f-c65c-4d4c-8f21-bc487d6810b9'
api_secret = '31D6C65EBAE64F25BBA219C9A7A2EE22'
api_passphrase = 'Pavelblackred+!5075782'

# URL для запроса данных о последней цене BTC/USDT
url = 'https://www.okex.com/api/v5/market/ticker?instId=BTC-USDT'

# Создание подписи
timestamp = str(int(time.time() * 1000))
method = 'GET'
request_path = '/api/v5/market/ticker'
body = ''
prehash_string = timestamp + method + request_path + body
signature = base64.b64encode(hmac.new(api_secret.encode(), prehash_string.encode(), hashlib.sha256).digest()).decode()

# Заголовки запроса
headers = {
    'OK-ACCESS-KEY': api_key,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': api_passphrase,
    'Content-Type': 'application/json'
}

# Отправка запроса
response = requests.get(url, headers=headers)
data = response.json()

# Получение последней цены BTC/USDT
last_price = data['data'][0]['last']

print(f'Последняя цена BTC/USDT: {last_price} USDT')
