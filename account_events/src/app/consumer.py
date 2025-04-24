import asyncio
from app.broker import broker
from app.websocket import OKXWebsocketsChannel
from app.redis_storage import get_connection, store_connection

@broker.subscriber("websocket_tasks")
async def websocket_task(config: dict):
    """Открывает WebSocket-соединение пользователя и сохраняет подписки в Redis"""
    user_id = config["user_id"]
    store_connection(user_id, config)

    ws_channel = OKXWebsocketsChannel(config)
    await ws_channel.subscribe_to_updates()

@broker.subscriber("update_subscriptions")
async def update_subscriptions(data: dict):
    """Обновляет подписки пользователя без разрыва соединения"""
    user_id = data["user_id"]
    config = get_connection(user_id)
    if config:
        config.update(data)
        store_connection(user_id, config)
        ws_channel = OKXWebsocketsChannel(config)
        await ws_channel._subscribe_channels()
        print(f"[{user_id}] Подписки обновлены: {config}")

async def restart_lost_connections():
    """Перезапускает WebSocket при падении соединения, используя Redis"""
    while True:
        await asyncio.sleep(10)  # Проверка каждые 10 секунд
        for key in redis_client.keys("user_connection:*"):
            user_id = key.decode().split(":")[-1]
            config = get_connection(user_id)
            if config:
                print(f"⚠️ [{user_id}] Обнаружено отключённое соединение. Перезапуск...")
                ws_channel = OKXWebsocketsChannel(**config)
                await ws_channel.subscribe_to_updates()


async def restore_connections():
    """При запуске сервиса пытается восстановить все соединения из Redis"""
    await asyncio.sleep(2)  # Даем сервису немного времени для запуска
    print("🔍 Проверка Redis на активные подключения...")
    
    for key in redis_client.keys("user_connection:*"):
        user_id = key.decode().split(":")[-1]
        config = get_connection(user_id)
        if config:
            print(f"🚀 Восстановление WebSocket для {user_id}...")
            ws_channel = OKXWebsocketsChannel(config)
            await ws_channel.subscribe_to_updates()
    
    print("✅ Восстановление завершено!")
