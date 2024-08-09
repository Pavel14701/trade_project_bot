import asyncio, contextlib, aiofiles
from abc import ABC, abstractmethod
from typing import Union, Optional
from datetime import datetime
from docx import Document


class ApiUtilsAsync(ABC):
    async def __create_timestamp_async(self, time: Union[str, int] = None) -> Optional[int]:
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


    async def __async_generator(self, data):
        for item in data:
            await asyncio.sleep(0)
            yield item


    @abstractmethod
    async def validate_get_data_params_async(self, limit:int = None, before: Optional[str] = None, after: Optional[str] = None) -> dict:
        with contextlib.suppress(Exception):
            load_data_after = await self.__create_timestamp_async(load_data_after)
        with contextlib.suppress(Exception):
            load_data_before = await self.__create_timestamp_async(load_data_before)
        if limit > 300:
            raise ValueError('Length 300 is max')
        if limit is None or (after is not None and before is not None):
            raise ValueError('Check params for get market data download')
        return {'limit': limit or ' ', 'before': before or ' ', 'after': after or ' '}

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