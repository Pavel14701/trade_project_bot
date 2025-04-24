from account_events.src.app.broker import broker

async def send_event(user_id: int, message: str):
    """Отправляет событие в RabbitMQ"""
    await broker.publish({"user_id": user_id, "message": message}, queue="account_events")
