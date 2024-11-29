import json, contextlib, time, hmac, base64, hashlib, websockets
from configs.load_settings import ConfigsProvider
from baselogs.custom_logger import create_logger
from listners.ivent_listner import OKXIventListner
from typing import Optional


pos_logger = create_logger('WsPositionsOKX')
ac_logger = create_logger('WsAccountOKX')
event_logger = create_logger('WsEventsOKX')



class OKXWebsocketsChannel:
    def __init__(self, instType:str='ANY', account:Optional[bool]=None, positions:Optional[bool]=True, liq_warning:Optional[bool]=None):
        settings = ConfigsProvider()
        api_settings = settings.load_api_configs()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.account, self.positions, self.liq_warning = account, positions, liq_warning
        self.instType = instType
                
        
        
    async def subscribe_to_updates(self) -> None:
        # private
        await self.__create_signature_ws()
        async with websockets.connect('wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999') as self.websocket:
            await self.__login()
            if self.account:
                await self.__subscribe_account_channel()
            if self.positions:
                await self.__subscribe_positions_channel()
            if self.liq_warning:
                await self.__subscribe_liq_warns_channel()
            await self.__catch_message()


    async def __create_signature_ws(self) -> None:
        self.timestamp = int(time.time())
        sign = f'{self.timestamp}GET/users/self/verify'
        self.signature = str(base64.b64encode(hmac.new(bytes(self.secret_key, encoding='utf-8'),\
            bytes(sign, encoding='utf-8'), digestmod=hashlib.sha256).digest()), 'utf-8')


    async def __login(self) -> None:
        msg = {'op': 'login', 'args': [{'apiKey': self.api_key, 'passphrase': self.passphrase,\
            'timestamp': self.timestamp,'sign': self.signature}]}
        await self.websocket.send(json.dumps(msg))
        response = await self.websocket.recv()
        event_logger.info(f'\nEvent,:{response}')


    async def __subscribe_account_channel(self) -> None:
        subs = {'op': 'subscribe', 'args': [{'channel': 'account', 'extraParams': '{\"updateInterval\": \"0\"}'}]}
        await self.websocket.send(json.dumps(subs))


    async def __subscribe_positions_channel(self) -> None:
        subs = {'op': 'subscribe', 'args': [{'channel': 'positions', 'instType': self.instType, 'extraParams':\
            '{\"updateInterval\": \"0\"}'}]}
        await self.websocket.send(json.dumps(subs))


    async def __subscribe_liq_warns_channel(self) -> None:
        subs = {'op': 'subscribe', 'args': [{'channel': 'liquidation-warning', 'instType': self.instType}]}
        await self.websocket.send(json.dumps(subs))


    async def __catch_message(self) -> None:
        async for msg in self.websocket:
            msg = json.loads(msg)
            print(type(msg))
            print((f"\nEvent: {msg}"))
            with contextlib.suppress(Exception):
                if msg.get('arg', {}).get('channel') == 'positions':
                    pos_logger.info(f"\nEvent, response:\n{msg}")
                    await OKXIventListner().ivent_reaction(msg)