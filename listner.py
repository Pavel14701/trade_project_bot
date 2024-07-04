import asyncio
from User.WebsocketsChannel import OKXWebsocketsChannel


okx_channel = OKXWebsocketsChannel()
if __name__ == '__main__':
    asyncio.run(okx_channel.main())