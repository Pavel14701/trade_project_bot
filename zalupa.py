import asyncio, time
from threading import Thread
from User.WebsocketsChannel import OKXWebsocketsChannel
from User.UserTradeFunctions import PlaceOrders

okx_channel = OKXWebsocketsChannel()

def second_thread():  
    time.sleep(30)
    trade = PlaceOrders('buy', 'ETH-USDT-SWAP', 1, 'long', 20, 0.03, None, 3432.0)
    order_id, order_sl_id = trade.place_market_order()
    trade.check_position(order_id)
    trade.check_position(order_sl_id)

    
thread = Thread(target=second_thread)
thread.start()

# Запуск основной асинхронной функции
if __name__ == '__main__':
    asyncio.run(okx_channel.main())
    





