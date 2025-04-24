import asyncio, aiofiles
from abc import ABC, abstractmethod
from typing import Union, Optional, Any
from datetime import datetime
from docx import Document
from api.base.requests_links import TIMEFRAMES



class ApiUtilsAsync(ABC):
    def __init__(self, api_key:Optional[str]=None, secret_key:Optional[str]=None, passphrase:Optional[str]=None, timeframe:Optional[str]=None):
        self.timeframe = timeframe
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    async def __create_timestamp_async(self, time: Union[str, int] = None) -> int:
        if time is None or isinstance(time, int):
            return time
        formats = [
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H', '%Y-%m-%d', '%Y-%m',
            '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M', '%d-%m-%Y %H', '%d-%m-%Y', '%m-%Y']
        formated_time = None
        async for fmt in self.__async_generator(formats):
            try:
                date_time_obj = datetime.strptime(time, fmt)
                if fmt == '%Y-%m-%d':
                    date_time_obj = date_time_obj.replace(hour=0, minute=0, second=0)
                elif fmt == '%Y-%m-%d %H':
                    date_time_obj = date_time_obj.replace(minute=0, second=0)
                formated_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                break
            except ValueError:
                continue
        if not formated_time:
            raise ValueError(f'Failed to recognize date and time format: {time}\nAvailable formats: {formats}')
        date_time_obj = datetime.strptime(formated_time, '%Y-%m-%d %H:%M:%S')
        return int(date_time_obj.timestamp())


    async def __async_generator(self, data:Any) -> Any:
        for item in data:
            await asyncio.sleep(0)
            yield item


    @abstractmethod
    async def validate_get_data_params_async(self, timeframe:str, limit:int=None, before:Optional[str]=None, after:Optional[str]=None) -> dict:
        after = await self.__create_timestamp_async(after)
        before = await self.__create_timestamp_async(before)
        if limit > 300:
            raise ValueError('Length 300 is max')
        if limit is None or (after is not None and before is not None):
            raise ValueError('Check params for get market data download')
        return {'limit': limit or ' ', 'before': before or ' ', 'after': after or ' '}


    @abstractmethod
    def validate_timeframe_format(self):
        for timeframe in TIMEFRAMES:
            if timeframe == self.timeframe:
                return
            else:
                raise ValueError(f'Format {timeframe} is not supported, use the format from the list:\n{TIMEFRAMES}')

    @abstractmethod
    def check_private_params(self):
        params = [self.api_key, self.secret_key, self.passphrase, self.flag]
        if self.flag == '1':
            print('Used demo-trading mode')
        elif self.flag == '0':
            print('Used real-trading mode')
        for param_name, param_value in zip(['api_key', 'secret_key', 'passphrase', 'flag'], params):
            if param_value is None:
                raise ValueError(f"Check your private data for the following: {param_name}")
        


    @abstractmethod
    async def save_swap_docx(self, result:Optional[dict], filename:Optional[str]) -> None:
        doc = Document()
        doc.add_paragraph(str(result))
        temp_filename = 'temp.docx'
        doc.save(temp_filename)
        async with aiofiles.open(temp_filename, 'rb') as temp_file:
            content = await temp_file.read()
        async with aiofiles.open(filename, 'wb') as target_file:
            await target_file.write(content)