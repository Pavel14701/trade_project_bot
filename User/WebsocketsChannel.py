import logging, json, contextlib
import websockets, datetime
from User.LoadSettings import LoadUserSettingData
from datasets.database import create_classes, Base, AsyncSessionLocal
from datasets.ClassesCreation import TradeUserData
from utils.LoggingFormater import MultilineJSONFormatter
from utils.IventListner import OKXIventListner


ws_logger = logging.getLogger('websocket')
ws_logger.setLevel(logging.DEBUG)
ws_file_handler = logging.FileHandler("listner.log")
ws_file_handler.setFormatter(MultilineJSONFormatter())
ws_handler = logging.StreamHandler()
ws_handler.setFormatter(MultilineJSONFormatter())
ws_logger.addHandler(ws_file_handler)
ws_logger.addHandler(ws_handler)


class OKXWebsocketsChannel:
    def __init__(self):
        api_settings = LoadUserSettingData.load_api_setings()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        
        
    async def main(self):
        self.timestamp, self.signature = await LoadUserSettingData.create_signature_ws(self.secret_key)
        await create_classes(Base)
        msg = {
            "op": "login",
            "args": [
                {
                    "apiKey": self.api_key,
                    "passphrase": self.passphrase,
                    "timestamp": self.timestamp,
                    "sign": self.signature
                }
            ]
        }
        async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as websocket:
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            ws_logger.info(f'{datetime.datetime.now().isoformat()}\nConnected - Response: {response}')
            subs = {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "account",
                        "extraParams": "{\"updateInterval\": \"0\"}"
                    }
                ]
            }
            await websocket.send(json.dumps(subs))
            subs = {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "positions",
                        "instType": "ANY",
                        "extraParams": "{\"updateInterval\": \"0\"}"
                    }
                ]
            }
            await websocket.send(json.dumps(subs))
            async for msg in websocket:
                msg = json.loads(msg)
                print((f"{datetime.datetime.now().isoformat()}\nСобытие: {msg}"))
                print(type(msg))
                with contextlib.suppress(Exception):
                    if msg['arg']['channel'] == 'positions':
                        listner = OKXIventListner(AsyncSessionLocal=AsyncSessionLocal)
                        await listner.ivent_reaction(msg)
                    elif msg['event']:
                        ws_logger.info(f"\n\nEvent: {datetime.datetime.now().isoformat()} Responce:")
                        ws_logger.info(msg)