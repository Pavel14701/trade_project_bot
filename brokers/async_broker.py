#!/usr/bin/env python3
import asyncio
from configs.load_settings import ConfigsProvider
from listners.ivent_listner_async import OKXIventListnerAsync

settings = ConfigsProvider().load_user_configs()

async def main(settings:dict):
    listner_instance = OKXIventListnerAsync(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()

if __name__ == '__main__':
    asyncio.run(main(settings))