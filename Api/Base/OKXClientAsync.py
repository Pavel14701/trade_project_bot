from httpx import AsyncClient
from abc import ABC, abstractmethod
import contextlib
import hmac, base64, hashlib
from typing import Optional
from datetime import datetime, timezone


class OKXClientAsync(ABC, AsyncClient):
    def __init__(self, api_key:str='-1', secret_key:str='-1', passphrase:str='-1', flag:str='1', debug:bool='True', proxy:str=None):
        self.base_url = 'https://www.okx.com'
        AsyncClient.__init__(self, base_url=self._base_url, http2=True, proxy=proxy)
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.flag = flag
        self.debug = debug
        self.proxy = proxy


    @abstractmethod
    async def make_request_async(self, request_path:str, body:str, method:str) -> dict:
        if method == 'GET':
            request_path += self.__parse_params_to_str(params)
        if self.api_key != '-1':
            headers = await self.__create_headers(request_path, body, method)
        else:
            headers = await self.__create_headers_no_sign()
        if self.debug:
            print(f'{self.base_url}{request_path}')
            print(headers)
        if method == 'GET':
            result = await self.get(f'{self.base_url}{request_path}', headers=headers)
        elif method == 'POST':
            result = await self.post(f'{self.base_url}{request_path}', headers=headers)
        return result.json()


    async def __create_headers(self, request_path:Optional[str], body:Optional[str], method:Optional[str]) -> dict:
        timestamp = await self.__create_timestamp_headers_async()
        msg = f'{str(timestamp)}{str.upper(method)}{request_path}{body}'
        signature = await self.__create_signature(self.secret_key, msg)
        return {
            'Content-Type': 'aplication/json', 'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature, 'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase, 'x-simulated-trading': self.flag
        }


    async def __create_headers_no_sign(self) -> dict:
        return {'Content-Type': 'application/json', 'x-simulated-trading': self.flag}


    async def __create_signature(self, secret_key:str, msg:str):
        return base64.b64encode(hmac.new(bytes(secret_key, encoding='utf8'),\
            bytes(msg, encoding='utf-8'), digestmod='sha256'))


    async def __create_timestamp_headers_async(self):
        return datetime.now(timezone.utc).replace(tzinfo=None).isoformat('T', 'milliseconds') + 'Z'


    async def __parse_params_to_str(self):
        url = '?'
        for key, value in self.items():
            if(value != ''):
                url = url + str(key) + '=' + str(value) + '&'
        return url[:-1]





