# ЮПИТЕР
import datetime
import logging
import json
import time
import hmac
import hashlib
import base64
import asyncio
import websockets
import nest_asyncio
from okx.exceptions import OkxAPIException

ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("test.log")
ws_logger.addHandler(ws_file_handler)

passphrase = "Pavelblackred+!5075782"
secret_key = "31D6C65EBAE64F25BBA219C9A7A2EE22"
api_key = "0a485d9f-c65c-4d4c-8f21-bc487d6810b9"

timestamp = int(time.time())
sign = str(timestamp) + 'GET' + '/users/self/verify'
total_params = bytes(sign, encoding='utf-8')
signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
signature = base64.b64encode(signature)
signature = str(signature, 'utf-8')


async def main():
    msg = dict(
        op='login',
        args=[
            dict(
                apiKey=f'{api_key}',
                passphrase=f'{passphrase}',
                timestamp=f'{timestamp}',
                sign=f'{signature}'
            )]
    )
    async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as websocket:
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        ws_logger.info('Connected ' + datetime.datetime.now().isoformat())
        subs1 = dict(
            op='subscribe',
            args=[
                dict(
                    channel='account',
                    extraParams='{\"updateInterval\": \"0\"}'
                )]
        )
        subs2 = dict(
            op='subscribe',
            args=[
                dict(
                    channel='positions',
                    instType='ANY',
                    extraParams='{\"updateInterval\": \"0\"}'
                )]
        )
        # await websocket.send(json.dumps(subs1))
        await websocket.send(json.dumps(subs2))
        async for json_file in websocket:
            # if json_file
            msg = json.loads(json_file)
            try:
                arg_channel = msg['arg']['channel']
                if arg_channel == "positions":
                    data = dict(
                        data_instId=msg['data'][0]['instId'],
                        data_liqPx=msg['data'][0]['liqPx'],
                        data_avgPx=msg['data'][0]['avgPx'],
                        data_posSide=msg['data'][0]['posSide'],
                        data_posId=msg['data'][0]['posId'],
                        data_notionalUsd=msg['data'][0]['notionalUsd'],
                        data_lever=msg['data'][0]['lever'],
                        # data_twap = msg['data'][0]['twap'],
                        data_upl=msg['data'][0]['upl'],
                        data_pnl=msg['data'][0]['pnl'],

                    )
                    ws_logger.info(f'\n {data} \n \n')
                else:
                    ws_logger.info(f'\n {msg} \n \n')
            except:
                ws_logger.info(f'\n {msg} \n \n')

if __name__ == '__main__':
    try:
        nest_asyncio.apply()  # вызываем функцию nest_asyncio.apply()
        asyncio.run(main())  # заменяем loop.run_until_complete(main()) на asyncio.run(main())
    except KeyboardInterrupt as e:
        ws_logger.info(f'\n\n Бот остановлен вручную')
    except OkxAPIException as e:
        ws_logger.exception(f'\n\n{e}')
    except Exception as e:
        ws_logger.exception(f'\n\n{e}')