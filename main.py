# ЮПИТЕР
import datetime
import logging
import json
import time
import hmac
import hashlib
import base64
import os
import asyncio
import websockets
import nest_asyncio  # импортируем пакет nest_asyncio
from dotenv import load_dotenv

# load env
load_dotenv(".env")
passphrase = os.getenv("PASSPHRASE")
secret_key = os.getenv("SECRET_KEY")
api_key = os.getenv("API_KEY")

# logger
ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("test.log")
ws_logger.addHandler(ws_file_handler)

timestamp = int(time.time())
sign = str(timestamp) + 'GET' + '/users/self/verify'
total_params = bytes(sign, encoding='utf-8')
signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
signature = base64.b64encode(signature)
signature = str(signature, 'utf-8')

print("signature = {0}".format(signature))


async def main():
    msg = \
        {
            "op": "login",
            "args": [
                {
                    "apiKey": f'{api_key}',
                    "passphrase": f'{passphrase}',
                    "timestamp": f'{timestamp}',
                    "sign": f'{signature}'
                }
            ]
        }

    async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as websocket:
        print(msg)
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(response)
        ws_logger.info('Connected ' + datetime.datetime.now().isoformat())

        subs = dict(
            op='subscribe',
            args=[
                dict(
                    channel='account',
                    extraParams='{\"updateInterval\": \"0\"}'
                )]
        )
        await websocket.send(json.dumps(subs))

        async for msg in websocket:
            msg = json.loads(msg)
            print(msg)


if __name__ == '__main__':
    nest_asyncio.apply()  # вызываем функцию nest_asyncio.apply()
    asyncio.run(main())  # заменяем loop.run_until_complete(main()) на asyncio.run(main())
