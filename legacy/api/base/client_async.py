import hmac, base64, json, asyncio, logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from httpx import AsyncClient


class ClientAsync(AsyncClient, ABC):
    def __init__(self, init_url:str, api_key:str=None, secret_key:str=None, passphrase:str=None, flag:str='1', debug:bool=True, proxy:str=None, logger:Optional[logging.Logger]=None):
        self.init_url = init_url
        AsyncClient.__init__(self, base_url=self.init_url, http2=True, proxy=proxy)
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.flag = flag
        self.debug = debug
        self.proxy = proxy
        self.logger = logger


    async def __make_request_async(self, request_path:str, params:dict, method:str) -> dict:
        if method == 'GET':
            request_path += await self.__parse_params_to_str(params)
        timestamp = await self.__create_timestamp_headers_async()
        if self.api_key:
            body = json.dumps(params)
            headers = await self.__create_headers(request_path, body, method, timestamp)
        else:
            headers = await self.__create_headers_no_sign()
        if self.debug:
            self.logger.info(f'\n{self.init_url}{request_path}\n{headers}')
            print(f'{self.init_url}{request_path}')
            print(headers)
        return  await self.__request_async(method, request_path, headers)


    async def __request_async(self, method:str, request_path:str, headers:dict) -> dict:
        try:
            if method == 'GET':
                result = await self.get(f'{self.init_url}{request_path}', headers=headers)
                return {'status_code': result, 'result': result.json()}
            elif method == 'POST':
                result = await self.post(f'{self.init_url}{request_path}', headers=headers)
                return {'status_code': result, 'result': result.json()}
        except Exception as e:
            print(f'Error:{e} at request:\n{self.init_url}{request_path} with headers:\n{headers}')
            raise e
        


    @abstractmethod
    async def _request_with_params_async(self, method:str, request_path:str, params:str) -> dict:
        result = await self.__make_request_async(method, request_path, params)
        if self.debug:
            print(result['result'])
            self.__check_result(result)
        return result['result']


    @abstractmethod
    async def _request_without_params(self, method:str, request_path:str) -> dict:
        result = await self.__make_request_async(method, request_path, {})
        if self.debug:
            print(result)
        self.__check_result(result)
        return result


    async def __check_result(self, result:Dict[str, dict]):
        if result['result']['code'] != '0':
            raise ValueError(f'\n{result['status_code']}\nError, code:{result['result']['status_code']}\nMessage: {result['result']['msg']}')


    async def __create_headers(self, request_path:str, body:str, method:str, timestamp:str) -> dict:
        msg = f'{(timestamp)}{str.upper(method)}{request_path}{body}'
        signature = await self.__create_signature(msg)
        return {
            'Content-Type': 'aplication/json', 'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature, 'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase, 'x-simulated-trading': self.flag
        }


    async def __create_headers_no_sign(self) -> dict:
        return {'Content-Type': 'application/json', 'x-simulated-trading': self.flag}


    async def __create_signature(self, msg:str) -> bytes:
        return base64.b64encode((hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(msg, encoding='utf-8'), digestmod='sha256')).digest())


    async def __create_timestamp_headers_async(self) -> str:
        return datetime.now(timezone.utc).replace(tzinfo=None).isoformat('T', 'milliseconds') + 'Z'


    async def __parse_params_to_str(self, params:dict) -> str:
        url = '?'
        async for key, value in self.__async_generator(params.items()):
            if(value != ''):
                url = url + str(key) + '=' + str(value) + '&'
        return str(url[:-1])


    async def __async_generator(self, items:Any):
        for item in items:
            await asyncio.sleep(0)
            yield item